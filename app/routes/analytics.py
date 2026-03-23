"""
Analytics Routes for Order Service
REST API endpoints for analytics and reporting
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional, List, Dict, Any
from datetime import date, timedelta, datetime
from uuid import UUID
import os
import httpx

from ..database import get_db

RESTAURANT_SERVICE_URL = os.getenv("RESTAURANT_SERVICE_URL", "http://restaurant-service:8003")
from ..analytics_schemas.analytics import (
    RevenueAnalyticsResponse,
    PopularItemsResponse,
    DayPatternsResponse,
    CustomerPreferencesResponse,
    PredictionResponse,
    OrderVolumeResponse,
    CategoryPerformanceResponse,
    PeakHoursResponse,
    PeriodComparison,
    TopPerformersResponse,
    OrderTypeAnalysisResponse,
    CustomerBehaviorMetrics,
    AnalyticsErrorResponse
)
from ..services import analytics_service
from shared.utils.logger import setup_logger

logger = setup_logger("analytics-routes")

router = APIRouter()


# ============================================================================
# 1. Revenue Analytics
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/revenue",
    response_model=RevenueAnalyticsResponse,
    summary="Get revenue analytics",
    description="Retrieve revenue metrics grouped by day, week, or month"
)
async def get_revenue_analytics(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    group_by: str = Query("daily", regex="^(daily|weekly|monthly)$", description="Grouping method"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get revenue analytics with flexible grouping.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **group_by**: daily, weekly, or monthly

    **Returns:** Revenue metrics grouped by period
    """
    try:
        result = await analytics_service.get_revenue_analytics(
            db, restaurant_id, start_date, end_date, group_by
        )
        return result
    except Exception as e:
        logger.error(f"Revenue analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch revenue analytics: {str(e)}"
        )


# ============================================================================
# 2. Popular Items
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/popular-items",
    response_model=PopularItemsResponse,
    summary="Get popular menu items",
    description="Retrieve top-selling items with trend analysis"
)
async def get_popular_items(
    restaurant_id: UUID,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Maximum items to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular menu items ranked by sales with trend indicators.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **days**: Number of days to analyze (1-365)
    - **limit**: Maximum items to return (1-50)

    **Returns:** List of popular items with sales metrics and trends
    """
    try:
        items = await analytics_service.get_popular_items(
            db, restaurant_id, days, limit
        )
        return {
            "days": days,
            "items": items
        }
    except Exception as e:
        logger.error(f"Popular items error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch popular items: {str(e)}"
        )


# ============================================================================
# 3. Day-of-Week Patterns
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/day-patterns",
    response_model=DayPatternsResponse,
    summary="Get day-of-week patterns",
    description="Analyze sales patterns by day of week"
)
async def get_day_patterns(
    restaurant_id: UUID,
    weeks: int = Query(8, ge=4, le=52, description="Number of weeks to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze sales patterns for each day of the week.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **weeks**: Number of weeks to analyze (4-52)

    **Returns:** Sales patterns for Monday through Sunday
    """
    try:
        patterns = await analytics_service.get_day_patterns(
            db, restaurant_id, weeks
        )
        return {
            "weeks_analyzed": weeks,
            "patterns": patterns
        }
    except Exception as e:
        logger.error(f"Day patterns error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch day patterns: {str(e)}"
        )


# ============================================================================
# 4. Customer Preferences (Placeholder - requires customer_identification)
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/customer-preferences/{customer_id}",
    response_model=CustomerPreferencesResponse,
    summary="Get customer preferences",
    description="Retrieve customer's order history and personalized recommendations"
)
async def get_customer_preferences(
    restaurant_id: UUID,
    customer_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get customer preferences and personalized recommendations.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **customer_id**: Customer UUID, email, or phone

    **Returns:** Customer preferences and recommendations
    """
    # TODO: Implement after creating customer_identification utility
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Customer preferences endpoint will be implemented with prediction service"
    )


# ============================================================================
# 5. Demand Predictions (Placeholder - requires prediction_service)
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/predictions/demand",
    response_model=PredictionResponse,
    summary="Get demand predictions",
    description="Predict demand for menu items using ML (dynamic periods: 1 week to 12 months)"
)
async def get_demand_predictions(
    restaurant_id: UUID,
    period: str = Query(
        "2_weeks",
        regex="^(1_week|2_weeks|1_month|3_months|6_months|12_months)$",
        description="Prediction period"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Predict demand for menu items using Facebook Prophet ML.

    **Prediction Periods:**
    - **1_week**: 7 days ahead (requires 60 days history)
    - **2_weeks**: 14 days ahead (requires 90 days history)
    - **1_month**: 30 days ahead (requires 120 days history)
    - **3_months**: 90 days ahead (requires 180 days history)
    - **6_months**: 180 days ahead (requires 365 days history)
    - **12_months**: 365 days ahead (requires 730 days history)

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **period**: Prediction period (1_week to 12_months)

    **Returns:** Predicted quantities with confidence intervals
    """
    try:
        predictions = await analytics_service.get_demand_predictions(
            db, restaurant_id, period
        )
        return predictions
    except Exception as e:
        logger.error(f"Demand predictions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate demand predictions: {str(e)}"
        )


# ============================================================================
# 6. Order Volume Trends
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/order-volume",
    response_model=OrderVolumeResponse,
    summary="Get order volume trends",
    description="Analyze order volume trends with growth rates"
)
async def get_order_volume(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    group_by: str = Query(
        "daily",
        regex="^(hourly|daily|weekly|monthly)$",
        description="Grouping method"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Get order volume trends with period-over-period growth rates.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **group_by**: hourly, daily, weekly, or monthly

    **Returns:** Order volume metrics with growth rates
    """
    try:
        result = await analytics_service.get_order_volume(
            db, restaurant_id, start_date, end_date, group_by
        )
        return result
    except Exception as e:
        logger.error(f"Order volume error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order volume: {str(e)}"
        )


# ============================================================================
# 7. Category Performance
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/category-performance",
    response_model=CategoryPerformanceResponse,
    summary="Get category performance",
    description="Analyze performance by menu category"
)
async def get_category_performance(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance metrics for each menu category.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)

    **Returns:** Category performance metrics
    """
    try:
        categories = await analytics_service.get_category_performance(
            db, restaurant_id, start_date, end_date
        )
        return {
            "start_date": start_date,
            "end_date": end_date,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Category performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category performance: {str(e)}"
        )


# ============================================================================
# 8. Peak Hours Analysis
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/peak-hours",
    response_model=PeakHoursResponse,
    summary="Get peak hours analysis",
    description="Analyze order patterns by hour of day"
)
async def get_peak_hours(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze order patterns by hour of day to identify peak times.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)

    **Returns:** Hourly metrics with busiest and slowest hours
    """
    try:
        result = await analytics_service.get_peak_hours(
            db, restaurant_id, start_date, end_date
        )
        return result
    except Exception as e:
        logger.error(f"Peak hours error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch peak hours: {str(e)}"
        )


# ============================================================================
# 9. Sales Comparison
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/sales-comparison",
    response_model=PeriodComparison,
    summary="Get sales comparison",
    description="Compare current period with previous period"
)
async def get_sales_comparison(
    restaurant_id: UUID,
    period: str = Query(
        "week",
        regex="^(week|month|quarter|year)$",
        description="Comparison period"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare sales metrics between current and previous period.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **period**: week, month, quarter, or year

    **Returns:** Comparison metrics with growth percentages
    """
    try:
        result = await analytics_service.get_sales_comparison(
            db, restaurant_id, period
        )
        return result
    except Exception as e:
        logger.error(f"Sales comparison error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sales comparison: {str(e)}"
        )


# ============================================================================
# 10. Top Performers
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/top-performers",
    response_model=TopPerformersResponse,
    summary="Get top performing items",
    description="Get top items ranked by revenue, quantity, or orders"
)
async def get_top_performers(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    rank_by: str = Query(
        "revenue",
        regex="^(revenue|quantity|orders)$",
        description="Ranking method"
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum items to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top performing items with detailed metrics.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **rank_by**: revenue, quantity, or orders
    - **limit**: Maximum items to return (1-100)

    **Returns:** Ranked list of top performing items
    """
    try:
        items = await analytics_service.get_top_performers(
            db, restaurant_id, start_date, end_date, rank_by, limit
        )
        return {
            "start_date": start_date,
            "end_date": end_date,
            "rank_by": rank_by,
            "items": items
        }
    except Exception as e:
        logger.error(f"Top performers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top performers: {str(e)}"
        )


# ============================================================================
# 11. Order Type Analysis
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/order-type-breakdown",
    response_model=OrderTypeAnalysisResponse,
    summary="Get order type breakdown",
    description="Analyze orders by type (table vs online)"
)
async def get_order_type_breakdown(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze order distribution between table and online orders.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)

    **Returns:** Breakdown by order type with percentages
    """
    try:
        breakdown = await analytics_service.get_order_type_breakdown(
            db, restaurant_id, start_date, end_date
        )
        return {
            "start_date": start_date,
            "end_date": end_date,
            "breakdown": breakdown
        }
    except Exception as e:
        logger.error(f"Order type breakdown error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch order type breakdown: {str(e)}"
        )


# ============================================================================
# 12. Customer Behavior
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/customer-behavior",
    response_model=CustomerBehaviorMetrics,
    summary="Get customer behavior metrics",
    description="Analyze customer behavior patterns"
)
async def get_customer_behavior(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date for analysis"),
    end_date: date = Query(..., description="End date for analysis"),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze customer behavior including new vs returning customers.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)

    **Returns:** Customer behavior metrics
    """
    try:
        result = await analytics_service.get_customer_behavior(
            db, restaurant_id, start_date, end_date
        )
        return result
    except Exception as e:
        logger.error(f"Customer behavior error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch customer behavior: {str(e)}"
        )


# ============================================================================
# 13. Analytics Dashboard Summary
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics",
    summary="Get analytics dashboard summary",
    description="Get a comprehensive analytics summary for the dashboard"
)
async def get_analytics_dashboard(
    restaurant_id: UUID,
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive analytics summary for dashboard.

    **Parameters:**
    - **restaurant_id**: Restaurant UUID
    - **days**: Number of days to analyze (7-90, default 30)

    **Returns:** Dashboard summary with key metrics
    """
    try:
        from datetime import datetime, timedelta

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # Get revenue analytics
        revenue_data = await analytics_service.get_revenue_analytics(
            db, restaurant_id, start_date, end_date, "daily"
        )

        # Get popular items
        popular_items_data = await analytics_service.get_popular_items(
            db, restaurant_id, days, 10
        )

        # Get day patterns
        weeks = min(days // 7, 8)
        day_patterns_data = await analytics_service.get_day_patterns(
            db, restaurant_id, weeks
        )

        # Get order volume
        order_volume_data = await analytics_service.get_order_volume(
            db, restaurant_id, start_date, end_date, "daily"
        )

        # Get customer behavior
        customer_behavior_data = await analytics_service.get_customer_behavior(
            db, restaurant_id, start_date, end_date
        )

        # Calculate summary metrics
        total_revenue = revenue_data.get("total_revenue", 0)
        total_orders = revenue_data.get("total_orders", 0)
        avg_order_value = revenue_data.get("overall_avg_order_value", 0)

        # Get growth from order volume
        periods = order_volume_data.get("periods", [])
        recent_growth = 0
        if len(periods) >= 2:
            recent_count = periods[-1]["order_count"]
            previous_count = periods[-2]["order_count"]
            if previous_count > 0:
                recent_growth = round(((recent_count - previous_count) / previous_count) * 100, 2)

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "summary": {
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "avg_order_value": avg_order_value,
                "recent_growth_rate": recent_growth,
                "total_customers": customer_behavior_data.get("total_customers", 0)
            },
            "popular_items": popular_items_data[:5],  # Top 5
            "day_patterns": day_patterns_data,
            "revenue_trend": revenue_data.get("metrics", [])[-7:] if revenue_data.get("metrics") else []  # Last 7 days
        }
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics dashboard: {str(e)}"
        )


# ============================================================================
# 14. POS Reports (Daily / Weekly / Monthly)
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/reports",
    summary="Get POS reports",
    description="Daily, weekly, or monthly account close report with cash/card breakdown"
)
async def get_pos_reports(
    restaurant_id: UUID,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get POS account close report for a date range.

    Returns completed table orders with cash/card payment breakdown.
    """
    try:
        from sqlalchemy import func, cast, select
        from sqlalchemy.dialects.postgresql import DATE as PG_DATE
        from sqlalchemy.orm import selectinload
        from ..models import Order, OrderItem
        from shared.models.enums import OrderStatus

        query = (
            select(Order)
            .options(selectinload(Order.items))
            .where(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.COMPLETED,
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date,
            )
            .order_by(Order.created_at.desc())
        )

        result = await db.execute(query)
        orders = result.scalars().all()

        cash_orders = [o for o in orders if o.payment_method == 'cash']
        card_orders = [o for o in orders if o.payment_method == 'card']
        unknown_orders = [o for o in orders if o.payment_method not in ('cash', 'card')]

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": {
                "total_orders": len(orders),
                "total_revenue": round(sum(o.total for o in orders), 2),
                "cash_orders": len(cash_orders),
                "cash_total": round(sum(o.total for o in cash_orders), 2),
                "card_orders": len(card_orders),
                "card_total": round(sum(o.total for o in card_orders), 2),
                "unknown_orders": len(unknown_orders),
                "unknown_total": round(sum(o.total for o in unknown_orders), 2),
            },
            "orders": [
                {
                    "id": str(o.id),
                    "order_number": o.order_number,
                    "table_id": str(o.table_id) if o.table_id else None,
                    "created_at": o.created_at.isoformat(),
                    "completed_at": o.completed_at.isoformat() if o.completed_at else None,
                    "subtotal": round(o.subtotal, 2),
                    "tax": round(o.tax, 2),
                    "total": round(o.total, 2),
                    "total_amount": round(o.total, 2),
                    "payment_method": o.payment_method,
                    "items_count": len(o.items),
                    "items": [
                        {
                            "name": i.item_name,
                            "quantity": i.quantity,
                            "price": round(float(i.item_price), 2),
                        }
                        for i in o.items
                    ],
                }
                for o in orders
            ],
        }
    except Exception as e:
        logger.error(f"POS reports error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch report: {str(e)}"
        )


# ============================================================================
# 15. Inventory-Aware Predictions (stock shortfall per day)
# ============================================================================

@router.get(
    "/restaurants/{restaurant_id}/analytics/inventory-predictions",
    summary="Stock-aware demand predictions",
    description="Predict what menu items will be needed for each upcoming day and cross-reference with current inventory to show stock shortfalls"
)
async def get_inventory_predictions(
    restaurant_id: UUID,
    days_ahead: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Combines demand forecast with current inventory stock to show:
    - How many of each item is predicted to be ordered each day
    - What ingredients are needed (via recipes/BOM)
    - What's currently in stock
    - Shortfall: what needs to be purchased
    """
    try:
        # 1. Get demand forecast from existing prediction service
        from ..services import analytics_service
        demand = await analytics_service.get_demand_predictions(db, restaurant_id, "1_week")

        # 2. Fetch current inventory + recipes from restaurant-service
        async with httpx.AsyncClient(timeout=10.0) as client:
            inv_resp = await client.get(f"{RESTAURANT_SERVICE_URL}/api/v1/restaurants/{restaurant_id}/inventory/items")
            recipe_resp = await client.get(f"{RESTAURANT_SERVICE_URL}/api/v1/restaurants/{restaurant_id}/inventory/recipes")
            alerts_resp = await client.get(f"{RESTAURANT_SERVICE_URL}/api/v1/restaurants/{restaurant_id}/inventory/alerts")

        inventory = inv_resp.json() if inv_resp.status_code == 200 else []
        recipes = recipe_resp.json() if recipe_resp.status_code == 200 else []
        alerts = alerts_resp.json() if alerts_resp.status_code == 200 else {}

        # Index inventory by id
        inv_by_id = {i["id"]: i for i in inventory}

        # Build recipe map: menu_item_id -> [{ inventory_item_id, quantity_required, unit, name }]
        recipe_map: Dict[str, List[Dict]] = {}
        for r in recipes:
            mid = r["menu_item_id"]
            iid = r["inventory_item_id"]
            inv_item = inv_by_id.get(iid, {})
            recipe_map.setdefault(mid, []).append({
                "inventory_item_id": iid,
                "inventory_item_name": inv_item.get("name", "Unknown"),
                "quantity_required": r["quantity_required"],
                "unit": r["unit"],
                "current_stock": inv_item.get("quantity", 0),
            })

        # 3. Build day-by-day prediction with stock analysis
        today = datetime.utcnow().date()
        days_result = []

        # Use day_patterns from order history for simple day-of-week scaling
        day_patterns_raw = await analytics_service.get_day_patterns(db, restaurant_id)
        day_patterns = {}
        if hasattr(day_patterns_raw, "patterns"):
            for p in day_patterns_raw.patterns:
                day_patterns[p.get("day_of_week", p.get("day", ""))] = p.get("order_count", 1)

        # Get popular items for base demand
        popular_raw = await analytics_service.get_popular_items(db, restaurant_id, limit=20)
        items_demand = []
        if hasattr(popular_raw, "items"):
            items_demand = popular_raw.items

        # Build running stock depletion across the forecast window
        running_stock = {iid: data["quantity"] for iid, data in inv_by_id.items()}

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for offset in range(days_ahead):
            forecast_date = today + timedelta(days=offset + 1)
            weekday = day_names[forecast_date.weekday()]

            # Scale factor from day patterns (default 1.0)
            scale = day_patterns.get(weekday, day_patterns.get(str(forecast_date.weekday()), 1.0))
            if isinstance(scale, (int, float)) and scale > 0:
                max_scale = max(day_patterns.values()) if day_patterns else 1
                scale = scale / max_scale if max_scale > 0 else 1.0

            day_items = []
            for item in items_demand:
                item_name = item.get("item_name", item.get("name", ""))
                menu_item_id = item.get("menu_item_id", item.get("id", ""))
                avg_qty = item.get("avg_daily_quantity", item.get("total_quantity", 0))
                if hasattr(avg_qty, "__float__"):
                    avg_qty = float(avg_qty)

                predicted_qty = round(float(avg_qty or 0) * scale)

                # Check ingredients needed
                ingredients_needed = []
                can_make = predicted_qty  # how many we can make with current stock
                for ing in recipe_map.get(str(menu_item_id), []):
                    iid = ing["inventory_item_id"]
                    total_needed = ing["quantity_required"] * predicted_qty
                    available = running_stock.get(iid, 0)
                    shortfall = max(0.0, round(total_needed - available, 2))
                    possible_from_stock = int(available / ing["quantity_required"]) if ing["quantity_required"] > 0 else predicted_qty
                    can_make = min(can_make, possible_from_stock)

                    ingredients_needed.append({
                        "ingredient_id": iid,
                        "ingredient_name": ing["inventory_item_name"],
                        "needed": round(total_needed, 2),
                        "available": round(available, 2),
                        "shortfall": shortfall,
                        "unit": ing["unit"],
                        "status": "ok" if shortfall == 0 else "low",
                    })

                day_items.append({
                    "menu_item_id": str(menu_item_id),
                    "menu_item_name": item_name,
                    "predicted_quantity": predicted_qty,
                    "can_make_from_stock": max(0, can_make),
                    "shortfall_units": max(0, predicted_qty - can_make),
                    "ingredients": ingredients_needed,
                })

            # Deplete running stock for next day calculations
            for di in day_items:
                for ing in di["ingredients"]:
                    iid = ing["ingredient_id"]
                    if iid in running_stock:
                        running_stock[iid] = max(0.0, running_stock[iid] - ing["needed"])

            days_result.append({
                "date": forecast_date.isoformat(),
                "day": weekday,
                "items": day_items,
            })

        # 4. Aggregate total shortfalls across all days
        total_shortfalls: Dict[str, Dict] = {}
        for day in days_result:
            for item in day["items"]:
                for ing in item["ingredients"]:
                    if ing["shortfall"] > 0:
                        iid = ing["ingredient_id"]
                        if iid not in total_shortfalls:
                            total_shortfalls[iid] = {
                                "ingredient_id": iid,
                                "ingredient_name": ing["ingredient_name"],
                                "total_shortfall": 0.0,
                                "unit": ing["unit"],
                            }
                        total_shortfalls[iid]["total_shortfall"] = round(
                            total_shortfalls[iid]["total_shortfall"] + ing["shortfall"], 2
                        )

        return {
            "restaurant_id": str(restaurant_id),
            "forecast_days": days_ahead,
            "generated_at": datetime.utcnow().isoformat(),
            "days": days_result,
            "shopping_list": sorted(total_shortfalls.values(), key=lambda x: x["total_shortfall"], reverse=True),
            "alerts": alerts,
        }

    except Exception as e:
        logger.error(f"Inventory predictions error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate inventory predictions: {str(e)}"
        )

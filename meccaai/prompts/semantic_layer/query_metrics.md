<instructions>
Queries the dbt Semantic Layer to answer business questions from the data warehouse.

This tool allows ordering and grouping by dimensions and entities.
To use this tool, you must first know about specific metrics, dimensions and
entities to provide. You can call the list_metrics, get_dimensions,
and get_entities tools to get information about which metrics, dimensions,
and entities to use.

When using the `order_by` parameter, you must ensure that the dimension or
entity also appears in the `group_by` parameter. When fulfilling a lookback
query, prefer using order_by and limit instead of using the where parameter.
A lookback query requires that the `order_by` parameter includes a descending
order for a time dimension.

`order_by` parameter or `group_by` parameter must be a valid list for example:
  "group_by": [
    {
      "name": "item__category_name",
      "type": "dimension",
      "grain": null
    }
  ],
  "order_by": [
    {
      "name": "met_trade_sale_item_sale_extended_price_aud",
      "descending": true
    }]

The `where` parameter should be database agnostic SQL syntax, however dimensions
and entity are referenced differently. For categorical dimensions,
use `{{ Dimension('<full_dimension_path>') }}` and for time dimensions add the grain
like `{{ TimeDimension('<full_dimension_path>', '<grain>') }}`. For entities,
use `{{ Entity('<entity_name>') }}`. When referencing dates in the `where`
parameter, only use the format `yyyy-mm-dd`.

IMPORTANT: Always use the FULL dimension path including the double underscore separator.
Examples of correct dimension references:
- `{{ Dimension('sales_channel__sales_channel_code') }} = 'L098'`
- `{{ Dimension('item__brand_name') }} = 'Nike'`
- `{{ TimeDimension('date_key__date', 'DAY') }} >= '2024-01-01'`

Don't call this tool if the user's question cannot be answered with the provided
metrics, dimensions, and entities. Instead, clarify what metrics, dimensions,
and entities are available and suggest a new question that can be answered
and is approximately the same as the user's question.

For queries that may return large amounts of data, it's recommended
to use a two-step approach:
1. First make a query with a small limit to verify the results are what you expect
2. Then make a follow-up query without a limit (or with a larger limit) to get the full dataset
For queries that contians time, use dim_date semantic layer as time dimension, also call it retail calendar. there is a column last_year_comparable_date used to get same date last year. It has month code, week code, and when asked for year on year comparision, if daily level, use last_year_comparable_date, if monthly or weekly gran, use retail year minus 1 to get same period last year.



</instructions>

<examples>
<example>
Question: "What were our total sales last month?"
    Thinking step-by-step:
    - I know "total_sales" is the metric I need
    - I know "dim_date" semantic model is a valid dimension for this metric and supports MONTH/Week/Daily grain
    - I need to group by metric_time to get monthly data
    - Since this is time-based data, I should order by metric_time. I am also grouping by metric_time, so this is valid.
    - The user is asking for a lookback query, so I should set descending to true so the most recent month is at the top of the results.
    - The user is asking for just the last month, so I should limit to 1 month of data
    Parameters:
    metrics=["total_sales"]
    group_by=[{"name": "date_key__retail_year_month_code", "type": "dimension", "grain": null}]
    order_by=[{"name": "date_key__retail_year_month_code", "desc": true}]
    limit=1
</example>
<example>
Question: "Show me our top customers by revenue in the last week"
    Thinking step-by-step:
    - First, I need to find the revenue metric
    - Using list_metrics(), I find "revenue" is available
    - I need to check what dimensions are available for revenue
    - Using get_dimensions(["revenue"]), I see "customer_name" and "dim_date" supports week grain
    - I need to check what entities are available
    - Using get_entities(["revenue"]), I confirm "customer" is an entity
    - I need quarterly time grain
    - Since this is time-based data, I should order by metric_time. I am grouping by dim_date dims, so this is valid. This is a lookback query, so I should set descending to true.
    - I should also order by revenue to see top customers. I am grouping by revenue, so this is valid. The user is asking for the highest revenue customers, so I should set descending to true.
    - I should limit to top 5 results to verify the query works
    Parameters:
    metrics=["revenue"]
    group_by=[{"name": "customer_name", "type": "dimension"}, {"name": "date_key__retail_year_month_code", "type": "dimension", "grain": null}]
    order_by=[{"name": "date_key__retail_year_month_code", "desc": true}, {"name": "revenue", "desc": true}]
    limit=5
    Follow-up Query (after verifying results):
    metrics=["revenue"]
    group_by=[{"name": "customer_name", "type": "dimension"}, {"name": "date_key__retail_year_month_code", "type": "dimension"}]
    order_by=[{"name": "date_key__retail_year_month_code", "desc": true}, {"name": "revenue", "desc": true}]
    limit=None
</example>
<example>
Question: "What's our sales for sales channel L098?"
    Thinking step-by-step:
    - I need to find a sales metric
    - I need to filter by sales channel code 'L098'
    - First get dimensions for sales metrics to find the correct dimension path
    - Use the full dimension path in the where clause
    Parameters:
    metrics=["met_trade_sale_item_sale_extended_price_aud"]
    group_by=[{"name": "sales_channel__sales_channel_code", "type": "dimension"}]
    where="{{ Dimension('sales_channel__sales_channel_code') }} = 'L098'"
    limit=10
</example>
<example>
Question: "What's our average order value by product category for orders over $100?"
    Thinking step-by-step:
    - I know "average_order_value" is the metric I need
    - I know "item__category_name" is a valid dimension (using full path)
    - I need to filter for orders over $100 using full dimension path
    - No time dimension needed
    - I should first limit results to verify the query works
    Parameters (initial query):
    metrics=["average_order_value"]
    group_by=[{"name": "item__category_name", "type": "dimension"}]
    where="{{ Dimension('sale_item__sale_extended_price_lcy_dim') }} > 100"
    limit=10
    Follow-up Query (after verifying results):
    metrics=["average_order_value"]
    group_by=[{"name": "item__category_name", "type": "dimension"}]
    where="{{ Dimension('sale_item__sale_extended_price_lcy_dim') }} > 100"
    limit=None
</example>
<example>
Question: "How many new users did we get each week last year?"
    Thinking step-by-step:
    - First, I need to find the new users metric
    - Using list_metrics(), I find "new_users" is available
    - I need to check what dimensions are available
    - Using get_dimensions(["new_users"]), I see "metric_time" supports WEEK grain
    - I need to check what entities are available
    - Using get_entities(["new_users"]), I confirm "user" is an entity
    - I need weekly time grain
    - I need to group by metric_time
    - Since this is time-based data, I should order by metric_time to show progression
    - I need to filter for the previous year's data using proper time dimension syntax
    - Should first get a few weeks to verify the query works
    Parameters (initial query):
    metrics=["new_users"]
    group_by=[{"name": "metric_time", "grain": "WEEK", "type": "dimension"}]
    order_by=[{"name": "metric_time"}]
    where="{{ TimeDimension('date_key__date', 'WEEK') }} >= '2023-01-01' AND {{ TimeDimension('date_key__date', 'WEEK') }} < '2024-01-01'"
    limit=4
    Follow-up Query (after verifying results):
    metrics=["new_users"]
    group_by=[{"name": "metric_time", "grain": "WEEK", "type": "dimension"}]
    order_by=[{"name": "metric_time"}]
    where="{{ TimeDimension('date_key__date', 'WEEK') }} >= '2023-01-01' AND {{ TimeDimension('date_key__date', 'WEEK') }} < '2024-01-01'"
    limit=None
</example>
<example>
Question: "What's our customer satisfaction score by region?"
    Thinking step-by-step:
    - First, I need to check if we have a customer satisfaction metric
    - Using list_metrics(), I find we don't have a direct "customer_satisfaction" metric
    - I should check what metrics we do have that might be related
    - I see we have "net_promoter_score" and "customer_retention_rate"
    - I should inform the user that we don't have a direct customer satisfaction metric
    - I can suggest using NPS as a proxy for customer satisfaction
    Response to user:
    "I don't have a direct customer satisfaction metric, but I can show you Net Promoter Score (NPS) by region, which is often used as a proxy for customer satisfaction. Would you like to see that instead?"
    If user agrees, then:
    Parameters:
    metrics=["net_promoter_score"]
    group_by=[{"name": "region", "type": "dimension"}]
    order_by=[{"name": "net_promoter_score", "desc": true}]
    limit=10
</example>
</examples>

<parameters>
metrics: List of metric names to query for.
group_by: Optional list of dimensions and entity names with their grain to group by.
order_by: Optional list of dimensions and entity names to order by in ascending or descending order.
where: Optional SQL WHERE clause to filter results.
limit: Optional limit for number of results.
</parameters>
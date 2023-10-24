"""Menu component layout."""
import dash_bootstrap_components as dbc

menu_items = [
    dbc.DropdownMenuItem("Productivity pages", header=True),
    dbc.DropdownMenuItem("Dashboard page", href="/"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Analytics pages", header=True),
    dbc.DropdownMenuItem("Goals page", href="/goals"),
    dbc.DropdownMenuItem("Trends page", href="/trends"),
    dbc.DropdownMenuItem("All events page", href="/all"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Customization pages", header=True),
    dbc.DropdownMenuItem("Configuration page", href="/configuration"),
    dbc.DropdownMenuItem("Categories page", href="/configuration2"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Troubleshooting pages", header=True),
    dbc.DropdownMenuItem("Activity table", href="/activity"),
    dbc.DropdownMenuItem("Categories table", href="/categories"),
    dbc.DropdownMenuItem("URLs table", href="/urls"),
    dbc.DropdownMenuItem("Input tables", href="/inputs"),
    dbc.DropdownMenuItem("Milestones table", href="/milestones"),
    dbc.DropdownMenuItem("Conflicts page", href="/conflicts"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("Credits", header=True),
    dbc.DropdownMenuItem("Attributions page", href="/credits"),
]

layout = dbc.Col(dbc.DropdownMenu(
    label="Pages",
    nav=True,
    size="lg",
    menu_variant="dark",
    children=menu_items,
    style={"fontSize": "20px"}
), width='auto')

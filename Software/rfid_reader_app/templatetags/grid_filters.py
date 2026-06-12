from django import template

register = template.Library()

@register.filter
def get_cell(grid, args):
    try:
        row, col = args.split(',')
        return grid.get((row, int(col)))
    except (ValueError, AttributeError):
        return None
    
    
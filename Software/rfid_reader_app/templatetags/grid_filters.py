from django import template

# register = template.Library()

# @register.filter
# def get_cell(grid, args):
#     print(f"get_cell called with args='{args}'")  # ← ajoute ça
#     try:
#         row, col = args.split(',')
#         print(f"Looking for key: ('{row}', {col})")  # ← et ça
#         result = grid.get((row, int(col)))
#         print(f"Result: {result}")  # ← et ça
#         return result
#     except (ValueError, AttributeError) as e:
#         print(f"Error: {e}")
#         return None
    

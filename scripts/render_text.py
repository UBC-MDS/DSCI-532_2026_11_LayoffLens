# Refactor the render.text function for summary 
# statistics with a helper function to reduce 
# the repetition in edge cases of the code

def get_rendered_text(data, column, term):
    statistic = data[column].sum()
    if statistic is None:
        return f"N/A"
    
    return f"{term}: {statistic:,}"
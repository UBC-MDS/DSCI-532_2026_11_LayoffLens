# Refactor the render.text function for summary 
# statistics with a helper function to reduce 
# the repetition in the code

def get_rendered_text(data, column, term):
    statistic = data[column].sum().execute()

    if statistic is None:
        return f"{term} Not Available"
    
    return f"{term}: {statistic:,}"
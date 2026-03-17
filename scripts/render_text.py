# Refactor the render.text function for summary 
# statistics with a helper function to reduce 
# the repetition in edge cases of the code

def get_rendered_text(statistic, term):
    if statistic is None:
        return f"{term} Not Available"
    
    return f"{term}: {statistic:,}"
from difflib import SequenceMatcher

def get_similarity_score(item1, item2):
    """Calculates a similarity score between two strings."""
    return SequenceMatcher(None, item1, item2).ratio()

def find_best_match(item, list_of_items):
    best_match = None
    best_score = 0
    min_score_threshold = 1.5  # Out of 3, adjust as needed, lower means more matches


    for candidate in list_of_items:
        # Calculate similarity score for each corresponding part (last name, first name, DOB)
        last_name_score = get_similarity_score(item[0], candidate[0])
        first_name_score = get_similarity_score(item[1], candidate[1])
        dob_match = candidate[2] == item[2]
        if dob_match:    
            dob_score = 1
        else:
            dob_score = 0
        
        # Add scores together
        total_score = last_name_score + first_name_score + dob_score
        

        # Update the best match if this one has a higher score
        if total_score > best_score:
            best_match = candidate
            best_score = total_score
    
    # Check if the best score meets the minimum threshold
    if best_score >= min_score_threshold:
        return best_match, best_score, item
    else:
        return "no match", best_score, item



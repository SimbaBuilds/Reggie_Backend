

def fetch_unread_with_label(label_id, gmail_service, page_token):
    response = gmail_service.users().messages().list(
        userId='me', 
        labelIds=[label_id, 'UNREAD'],
        pageToken=page_token
    ).execute()

    return response

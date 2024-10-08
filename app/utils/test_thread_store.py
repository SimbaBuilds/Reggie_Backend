# test_thread_store.py

from thread_store import store_thread_info, is_thread_id_stored, remove_thread_info

def test_thread_store():
    thread_id = 'test_thread_id'
    history_id = 'test_history_id'

    # Store thread info
    store_thread_info(thread_id, history_id)
    assert is_thread_id_stored(thread_id) == True
    print("Thread ID stored successfully.")

    # Remove thread info
    remove_thread_info(thread_id)
    assert is_thread_id_stored(thread_id) == False
    print("Thread ID removed successfully.")

if __name__ == '__main__':
    test_thread_store()
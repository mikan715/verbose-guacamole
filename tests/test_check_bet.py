import pytest
from unittest.mock import Mock, patch
from main import check_bet

@pytest.fixture
def mock_collections():
    with patch('main.collection_users') as mock_users, \
         patch('main.collection_fixturesBL') as mock_fixtures, \
         patch('main.shared_data_frontend') as mock_shared_data:
        
        # Setup shared data
        mock_shared_data.get.return_value = "testuser"
        
        # Setup mock user data
        mock_user = {
            "name": "testuser",
            "balance": 100.0,
            "bets": [
                {
                    "fixture": 123,
                    "wettgeld": 10.0,
                    "odd": "Home",
                    "value": 2.0,
                    "checked_bet": False
                }
            ]
        }
        mock_users.find_one.return_value = mock_user
        
        yield {
            "users": mock_users,
            "fixtures": mock_fixtures,
            "shared_data": mock_shared_data
        }

def test_check_bet_home_win(mock_collections):
    # Setup fixture data for a home win
    mock_fixture = {
        "teams": {
            "home": {"winner": True},
            "away": {"winner": False}
        }
    }
    mock_collections["fixtures"].find_one.return_value = mock_fixture
    
    # Execute function
    check_bet()
    
    # Verify the balance was updated correctly
    mock_collections["users"].update_one.assert_called_once()
    update_call = mock_collections["users"].update_one.call_args[0]
    assert update_call[0] == {"name": "testuser", "bets.fixture": 123}
    assert update_call[1]["$set"]["balance"] == 120.0  # 100 + (10 * 2.0)
    assert update_call[1]["$set"]["bets.$.checked_bet"] is True

def test_check_bet_no_win(mock_collections):
    # Setup fixture data for a loss
    mock_fixture = {
        "teams": {
            "home": {"winner": False},
            "away": {"winner": True}
        }
    }
    mock_collections["fixtures"].find_one.return_value = mock_fixture
    
    # Execute function
    check_bet()
    
    # Verify no balance update occurred
    mock_collections["users"].update_one.assert_not_called()

def test_check_bet_no_fixture(mock_collections):
    # Setup mock to return no fixture
    mock_collections["fixtures"].find_one.return_value = None
    
    # Execute function
    check_bet()
    
    # Verify no balance update occurred
    mock_collections["users"].update_one.assert_not_called() 
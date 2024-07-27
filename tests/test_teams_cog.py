import pytest
import random
from cogs.teams import generate_teams

class MockMember:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"MockMember({self.name})"


def test_generate_quads_even_members():
    total_members = 8
    team_size = 4
    members = [MockMember(f"Member{i}") for i in range(total_members)]
    teams = generate_teams(team_size, members)
    
    assert len(teams) == total_members // team_size
    for team in teams:
        assert len(team) == team_size

def test_quads_one_extra():
    members = [MockMember(f"Member{i}") for i in range(5)]
    team_size = 4
    teams = generate_teams(team_size, members)
    
    assert len(teams) == 2
    for team in teams:
        assert len(team) >= 2

def test_quads_two_extra():
    members = [MockMember(f"Member{i}") for i in range(6)]
    team_size = 4
    teams = generate_teams(team_size, members)
    
    assert len(teams) == 2
    for team in teams:
        assert len(team) <= 3

def test_quads_three_extra():
    members = [MockMember(f"Member{i}") for i in range(12)]
    team_size = 4
    teams = generate_teams(team_size, members)
    
    for team in teams:
        assert len(team) >= 3

def test_generate_duos_even_members():
    members = [MockMember(f"Member{i}") for i in range(8)]
    team_size = 2
    teams = generate_teams(team_size, members)
    
    assert len(teams) == 8 // team_size
    for team in teams:
        assert len(team) == team_size

def test_duos_one_extra():
    members = [MockMember(f"Member{i}") for i in range(5)]  
    team_size = 2
    teams = generate_teams(team_size, members)
    
    assert len(teams) == 3
    for team in teams:
        assert len(team) <= 2


if __name__ == "__main__":
    pytest.main()

from cogs.teams import generate_teams
import random


class MockMember:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"MockMember({self.name})"


def test_quads_full_teams():
    """Test generating full teams of 4"""
    team_size = 4
    random_amt_members = [team_size * i for i in range(10)]
    total_members = random.choice(random_amt_members)
    members = [MockMember(f"Member{i}") for i in range(total_members)]
    teams = generate_teams(team_size, members)

    assert len(teams) == total_members // team_size
    for team in teams:
        assert len(team) == team_size


def test_quads_one_extra():
    """Test generating teams with one extra member"""
    team_size = 4

    # Generate random amount of members divisible by 4, to test multiple scenarios
    random_amt_members = [team_size * i for i in range(1, 10)]

    for total_members in random_amt_members:
        # Add one extra member
        total_members_with_extra = total_members + 1
        members = [MockMember(f"Member{i}") for i in range(total_members_with_extra)]
        teams = generate_teams(team_size, members)

        # if 5 members, there should be 2 teams, each with 2 or 3 members
        if total_members_with_extra == 5:
            assert len(teams) == 2
            for team in teams:
                assert len(team) >= 2
        # Otherwise, teams should have no less than 3 members
        else:
            for team in teams:
                assert len(team) >= 3
                assert len(team) <= 4


def test_quads_two_extra():
    """Test generating teams with two extra members"""
    team_size = 4

    # Generate random amount of members divisible by 4, to test multiple scenarios
    random_amt_members = [team_size * i for i in range(1, 10)]

    for total_members in random_amt_members:
        # Add two extra members
        total_members_with_extra = total_members + 2
        members = [MockMember(f"Member{i}") for i in range(total_members_with_extra)]
        teams = generate_teams(team_size, members)

        # if 6 members, there should be 2 teams, each with 3 members
        if total_members_with_extra == 6:
            assert len(teams) == 2
            for team in teams:
                assert len(team) == 3
        # Otherwise, teams should have no less than 3 members and no more than 4
        else:
            for team in teams:
                assert len(team) >= 3
                assert len(team) <= 4


def test_quads_three_extra():
    """Test generating teams with three extra members"""
    team_size = 4

    # Generate random amount of members divisible by 4, to test multiple scenarios
    random_amt_members = [team_size * i for i in range(1, 10)]

    for total_members in random_amt_members:
        # Add three extra members
        total_members_with_extra = total_members + 3
        members = [MockMember(f"Member{i}") for i in range(total_members_with_extra)]
        teams = generate_teams(team_size, members)

        # if 7 members, there should be 2 teams, one with 3 members and one with 4 members
        if total_members_with_extra == 7:
            assert len(teams) == 2
            for team in teams:
                assert len(team) >= 3

        # Otherwise, teams should have no less than 3 members
        for team in teams:
            assert len(team) >= 3
            assert len(team) <= 4


def test_generate_duos_even_members():
    """Test generating full teams of 2"""
    team_size = 2
    random_amt_members = [team_size * i for i in range(10)]
    total_members = random.choice(random_amt_members)
    members = [MockMember(f"Member{i}") for i in range(total_members)]
    teams = generate_teams(team_size, members)

    # In duos, with even number of members, there should be no teams with less than 2 members
    assert len(teams) == total_members // team_size
    for team in teams:
        assert len(team) == team_size


def test_duos_one_extra():
    """Test generating teams with one extra member"""
    team_size = 2

    # Generate random amount of members divisible by 2, to test multiple scenarios
    random_amt_members = [team_size * i for i in range(1, 10)]

    for total_members in random_amt_members:
        # Add one extra member
        total_members_with_extra = total_members + 1
        members = [MockMember(f"Member{i}") for i in range(total_members_with_extra)]
        teams = generate_teams(team_size, members)

        # if odd number of members, there should be teams of 2, and one team with 1 member
        if total_members_with_extra % 2 == 1:
            one_member_teams_count = sum(1 for team in teams if len(team) == 1)
            assert one_member_teams_count == 1
            for team in teams:
                assert len(team) >= 1

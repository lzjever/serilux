"""
Test deeply nested container structures with Serializable objects.

This test verifies that the implementation can handle complex nested structures like:
- dict containing list containing dict containing Serializable objects
- list containing dict containing list containing Serializable objects
- Multiple levels of nesting
"""

from serilux import (
    ObjectRegistry,
    Serializable,
    register_serializable,
)


@register_serializable
class Person(Serializable):
    """A simple Person class."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.name = ""
        self.age = 0
        self.add_serializable_fields(["_id", "name", "age"])


@register_serializable
class Team(Serializable):
    """Team with nested container structures."""

    def __init__(self):
        super().__init__()
        self._id = None
        self.name = ""
        # dict -> list -> dict -> Serializable
        self.departments = {}  # {dept_name: {role: [Person, Person, ...]}}
        # list -> dict -> list -> Serializable
        self.projects = []  # [{project_name: {phase: [Person, ...]}}]
        # dict -> dict -> list -> dict -> Serializable
        self.organizations = {}  # {org_name: {dept: {team: [Person]}}}
        self.add_serializable_fields(["_id", "name", "departments", "projects", "organizations"])


def test_dict_list_dict_serializable():
    """Test dict -> list -> dict -> Serializable structure."""
    team = Team()
    team._id = "team1"
    team.name = "Engineering"

    # Structure: departments[dept_name][role] = [Person, Person, ...]
    person1 = Person()
    person1._id = "p1"
    person1.name = "Alice"
    person1.age = 30

    person2 = Person()
    person2._id = "p2"
    person2.name = "Bob"
    person2.age = 25

    team.departments = {
        "backend": {
            "senior": [person1],
            "junior": [person2],
        },
        "frontend": {
            "senior": [person1],  # Same person in different roles
        },
    }

    # Serialize
    data = team.serialize()
    print(f"\nSerialized structure: {list(data['departments'].keys())}")

    # Deserialize
    new_team = Team()
    registry = ObjectRegistry()
    registry.register(new_team, object_id="team1")
    new_team.deserialize(data, registry=registry)

    # Verify structure
    assert new_team.departments is not None
    assert "backend" in new_team.departments
    assert "senior" in new_team.departments["backend"]
    assert len(new_team.departments["backend"]["senior"]) == 1
    assert new_team.departments["backend"]["senior"][0].name == "Alice"
    assert new_team.departments["backend"]["senior"][0].age == 30

    # Verify objects were registered
    assert registry.find_by_id("p1") is not None
    assert registry.find_by_id("p2") is not None

    print("✅ dict -> list -> dict -> Serializable: PASSED")


def test_list_dict_list_serializable():
    """Test list -> dict -> list -> Serializable structure."""
    team = Team()
    team._id = "team2"
    team.name = "Product"

    person1 = Person()
    person1._id = "p3"
    person1.name = "Charlie"
    person1.age = 35

    person2 = Person()
    person2._id = "p4"
    person2.name = "David"
    person2.age = 28

    # Structure: projects = [{project_name: {phase: [Person, ...]}}]
    team.projects = [
        {
            "project_a": {
                "phase1": [person1],
                "phase2": [person2],
            }
        },
        {
            "project_b": {
                "phase1": [person1, person2],  # Multiple people
            }
        },
    ]

    # Serialize
    data = team.serialize()
    print(f"\nSerialized projects: {len(data['projects'])} projects")

    # Deserialize
    new_team = Team()
    registry = ObjectRegistry()
    registry.register(new_team, object_id="team2")
    new_team.deserialize(data, registry=registry)

    # Verify structure
    assert len(new_team.projects) == 2
    assert "project_a" in new_team.projects[0]
    assert "phase1" in new_team.projects[0]["project_a"]
    assert len(new_team.projects[0]["project_a"]["phase1"]) == 1
    assert new_team.projects[0]["project_a"]["phase1"][0].name == "Charlie"

    assert "project_b" in new_team.projects[1]
    assert len(new_team.projects[1]["project_b"]["phase1"]) == 2

    # Verify objects were registered
    assert registry.find_by_id("p3") is not None
    assert registry.find_by_id("p4") is not None

    print("✅ list -> dict -> list -> Serializable: PASSED")


def test_dict_dict_list_dict_serializable():
    """Test dict -> dict -> list -> dict -> Serializable structure (4 levels)."""
    team = Team()
    team._id = "team3"
    team.name = "Enterprise"

    person1 = Person()
    person1._id = "p5"
    person1.name = "Eve"
    person1.age = 40

    person2 = Person()
    person2._id = "p6"
    person2.name = "Frank"
    person2.age = 32

    # Structure: organizations[org_name][dept][team] = [Person]
    team.organizations = {
        "company_a": {
            "engineering": {
                "team_alpha": [person1],
            },
            "sales": {
                "team_beta": [person2],
            },
        },
        "company_b": {
            "engineering": {
                "team_gamma": [person1, person2],
            },
        },
    }

    # Serialize
    data = team.serialize()
    print(f"\nSerialized organizations: {list(data['organizations'].keys())}")

    # Deserialize
    new_team = Team()
    registry = ObjectRegistry()
    registry.register(new_team, object_id="team3")
    new_team.deserialize(data, registry=registry)

    # Verify structure (4 levels deep)
    assert "company_a" in new_team.organizations
    assert "engineering" in new_team.organizations["company_a"]
    assert "team_alpha" in new_team.organizations["company_a"]["engineering"]
    assert len(new_team.organizations["company_a"]["engineering"]["team_alpha"]) == 1
    assert new_team.organizations["company_a"]["engineering"]["team_alpha"][0].name == "Eve"

    assert "company_b" in new_team.organizations
    assert len(new_team.organizations["company_b"]["engineering"]["team_gamma"]) == 2

    # Verify objects were registered
    assert registry.find_by_id("p5") is not None
    assert registry.find_by_id("p6") is not None

    print("✅ dict -> dict -> list -> dict -> Serializable (4 levels): PASSED")


def test_mixed_nested_structures():
    """Test mixed nested structures in the same object."""
    team = Team()
    team._id = "team4"
    team.name = "Mixed Team"

    # Create multiple people
    people = []
    for i in range(5):
        person = Person()
        person._id = f"person_{i}"
        person.name = f"Person{i}"
        person.age = 20 + i
        people.append(person)

    # Mix all structures
    team.departments = {
        "dept1": {
            "role1": [people[0], people[1]],
        }
    }

    team.projects = [
        {
            "proj1": {
                "phase1": [people[2], people[3]],
            }
        }
    ]

    team.organizations = {
        "org1": {
            "dept1": {
                "team1": [people[4]],
            }
        }
    }

    # Serialize
    data = team.serialize()

    # Deserialize
    new_team = Team()
    registry = ObjectRegistry()
    registry.register(new_team, object_id="team4")
    new_team.deserialize(data, registry=registry)

    # Verify all structures
    assert len(new_team.departments["dept1"]["role1"]) == 2
    assert len(new_team.projects[0]["proj1"]["phase1"]) == 2
    assert len(new_team.organizations["org1"]["dept1"]["team1"]) == 1

    # Verify all people were registered
    for i in range(5):
        assert registry.find_by_id(f"person_{i}") is not None

    print("✅ Mixed nested structures: PASSED")


def test_empty_containers():
    """Test empty containers at various levels."""
    team = Team()
    team._id = "team5"
    team.name = "Empty Team"

    # Empty containers
    team.departments = {}
    team.projects = []
    team.organizations = {}

    # Serialize and deserialize
    data = team.serialize()
    new_team = Team()
    registry = ObjectRegistry()
    registry.register(new_team, object_id="team5")
    new_team.deserialize(data, registry=registry)

    # Verify empty structures are preserved
    assert new_team.departments == {}
    assert new_team.projects == []
    assert new_team.organizations == {}

    print("✅ Empty containers: PASSED")


def test_nested_with_methods():
    """Test nested containers with Serializable objects that have methods."""
    from serilux import register_serializable

    @register_serializable
    class NestedProcessor(Serializable):
        def __init__(self):
            super().__init__()
            self._id = None
            self.name = ""
            self.process = self.process_data
            self.add_serializable_fields(["_id", "name", "process"])

        def process_data(self, data):
            return data.upper()

    @register_serializable
    class NestedProcessorGroup(Serializable):
        def __init__(self):
            super().__init__()
            self._id = None
            self.name = ""
            # dict -> list -> Serializable (with methods)
            self.processors = {}  # {group_name: [NestedProcessor, NestedProcessor, ...]}
            self.add_serializable_fields(["_id", "name", "processors"])

    group = NestedProcessorGroup()
    group._id = "group1"
    group.name = "Processing Group"

    proc1 = NestedProcessor()
    proc1._id = "proc1"
    proc1.name = "Processor1"

    proc2 = NestedProcessor()
    proc2._id = "proc2"
    proc2.name = "Processor2"

    # Nested structure with methods
    group.processors = {
        "group_a": [proc1, proc2],
        "group_b": [proc1],  # Same processor in different groups
    }

    # Serialize
    data = group.serialize()

    # Deserialize
    new_group = NestedProcessorGroup()
    registry = ObjectRegistry()
    registry.register(new_group, object_id="group1")
    new_group.deserialize(data, registry=registry)

    # Verify structure
    assert len(new_group.processors["group_a"]) == 2
    assert new_group.processors["group_a"][0].name == "Processor1"

    # Verify methods work (this tests that objects were registered)
    assert new_group.processors["group_a"][0].process("test") == "TEST"
    assert new_group.processors["group_a"][1].process("hello") == "HELLO"

    # Verify objects were registered
    assert registry.find_by_id("proc1") is not None
    assert registry.find_by_id("proc2") is not None

    print("✅ Nested containers with methods: PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Deeply Nested Container Structures")
    print("=" * 60)

    test_dict_list_dict_serializable()
    test_list_dict_list_serializable()
    test_dict_dict_list_dict_serializable()
    test_mixed_nested_structures()
    test_empty_containers()
    test_nested_with_methods()

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

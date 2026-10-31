"""Worksheet-based English comprehension questions for October 2026.

Each concept has one question. Image-backed answers show all three candidates;
family questions use a neutral group scene rather than identifying pictured faces.
Choice keys are semantic identifiers, independent of their displayed positions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Choice:
    key: str
    label: str
    image: str = ""


@dataclass(frozen=True)
class Item:
    key: str
    category: str
    question: str
    choices: tuple[Choice, ...]
    correct: str
    explanation: str
    image: str = ""


CLASSROOM = Choice("classroom", "Classroom", "classroom")
PLAYGROUND = Choice("playground", "Playground", "playground")
LIBRARY = Choice("library", "Library", "library")
LAB = Choice("lab", "Lab", "lab")
GYM = Choice("gym", "Gym", "gym")
CANTEEN = Choice("canteen", "Canteen", "canteen")
RECEPTION = Choice("reception", "Reception", "reception")
TOILETS = Choice("toilets", "Toilets", "toilets")
ART_ROOM = Choice("art-room", "Art room", "art-room")
NURSE_OFFICE = Choice("nurse-office", "Nurse's office", "nurse-office")

TEACHER = Choice("teacher", "Teacher", "teacher")
HEADMASTER = Choice("headmaster", "Headmaster", "headmaster")
SCHOOL_NURSE = Choice("school-nurse", "School nurse", "school-nurse")
COOK = Choice("cook", "Cook", "cook")
CARETAKER = Choice("caretaker", "Caretaker", "caretaker")
CLEANER = Choice("cleaner", "Cleaner", "cleaner")
RECEPTIONIST = Choice("receptionist", "Receptionist", "receptionist")
LIBRARIAN = Choice("librarian", "Librarian", "librarian")

MUM = Choice("mum", "Mum (mother)")
DAD = Choice("dad", "Dad (father)")
SISTER = Choice("sister", "Sister")
BROTHER = Choice("brother", "Brother")
GRANDMA = Choice("grandma", "Grandma (grandmother)")
GRANDPA = Choice("grandpa", "Grandpa (grandfather)")
BABY = Choice("baby", "Baby")
AUNT = Choice("aunt", "Aunt")
UNCLE = Choice("uncle", "Uncle")
COUSIN = Choice("cousin", "Cousin")
PET = Choice("pet", "Pet")

NEIGHBOURHOOD = Choice("neighbourhood", "Neighbourhood", "neighbourhood")
VILLAGE = Choice("village", "Village", "village")
TOWN = Choice("town", "Town", "town")
CITY = Choice("city", "City", "city")

MAYOR = Choice("mayor", "Mayor", "mayor")
DOCTOR = Choice("doctor", "Doctor", "doctor")
GARDENER = Choice("gardener", "Gardener", "gardener")
FIREFIGHTER = Choice("firefighter", "Firefighter", "firefighter")
POLICE_OFFICER = Choice("police-officer", "Police officer", "police-officer")
BUS_DRIVER = Choice("bus-driver", "Bus driver", "bus-driver")
POSTMAN = Choice("postman", "Postman", "postman")
STREET_CLEANER = Choice("street-cleaner", "Street cleaner", "street-cleaner")


ITEMS: tuple[Item, ...] = (
    Item(
        "place-classroom", "school-places",
        "Where does a class usually sit at desks to have lessons?",
        (CLASSROOM, CANTEEN, RECEPTION), "classroom",
        "Children have lessons with their teacher in the classroom.",
    ),
    Item(
        "place-playground", "school-places",
        "It is break time. Where can children play outside at school?",
        (GYM, PLAYGROUND, LIBRARY), "playground",
        "The playground is an outdoor place to play at school.",
    ),
    Item(
        "place-library", "school-places",
        "Where can you choose a school book to borrow and read?",
        (RECEPTION, ART_ROOM, LIBRARY), "library",
        "The library has books that children can read and borrow.",
    ),
    Item(
        "place-lab", "school-places",
        "Which room has special equipment for science experiments?",
        (LAB, GYM, CANTEEN), "lab",
        "A lab is a room equipped for science experiments.",
    ),
    Item(
        "place-gym", "school-places",
        "It is raining. Where can a class do indoor sports?",
        (PLAYGROUND, GYM, ART_ROOM), "gym",
        "The gym is an indoor place for exercise and sports.",
    ),
    Item(
        "place-canteen", "school-places",
        "Lunch is ready. Where do children go to eat their school meal?",
        (CLASSROOM, LAB, CANTEEN), "canteen",
        "Children eat their school meals in the canteen.",
    ),
    Item(
        "place-reception", "school-places",
        "A visitor arrives at school. Where should they go to be welcomed?",
        (RECEPTION, LIBRARY, NURSE_OFFICE), "reception",
        "Reception is where visitors are welcomed when they arrive.",
    ),
    Item(
        "place-toilets", "school-places",
        "You need to use the toilet at school. Where should you go?",
        (CANTEEN, TOILETS, RECEPTION), "toilets",
        "The toilets are the school facilities for using the toilet and washing hands.",
    ),
    Item(
        "place-art-room", "school-places",
        "Which room is set up for painting and making art?",
        (LAB, LIBRARY, ART_ROOM), "art-room",
        "The art room has space and materials for making art.",
    ),
    Item(
        "place-nurse-office", "school-places",
        "You feel ill at school. Where can the school nurse look after you?",
        (NURSE_OFFICE, CLASSROOM, GYM), "nurse-office",
        "The school nurse looks after children in the nurse's office.",
    ),
    Item(
        "worker-teacher", "school-workers",
        "Who explains a new lesson and helps the class learn?",
        (COOK, TEACHER, CARETAKER), "teacher",
        "A teacher teaches lessons and helps children learn.",
    ),
    Item(
        "worker-headmaster", "school-workers",
        "Who leads the whole school and its staff?",
        (LIBRARIAN, RECEPTIONIST, HEADMASTER), "headmaster",
        "The headmaster leads the school and its staff.",
    ),
    Item(
        "worker-school-nurse", "school-workers",
        "A child feels ill in class. Which school worker helps them?",
        (SCHOOL_NURSE, COOK, CLEANER), "school-nurse",
        "The school nurse looks after children who are ill or hurt at school.",
    ),
    Item(
        "worker-cook", "school-workers",
        "Who prepares the hot meals for the school canteen?",
        (CARETAKER, COOK, RECEPTIONIST), "cook",
        "The cook prepares food for school meals.",
    ),
    Item(
        "worker-caretaker", "school-workers",
        "A school door is broken. Who looks after the building and its repairs?",
        (TEACHER, CLEANER, CARETAKER), "caretaker",
        "The caretaker looks after the school building and deals with repairs.",
    ),
    Item(
        "worker-cleaner", "school-workers",
        "Whose job is to wash the school floors and keep the classrooms clean?",
        (CLEANER, LIBRARIAN, SCHOOL_NURSE), "cleaner",
        "The cleaner keeps the school's rooms and floors clean.",
    ),
    Item(
        "worker-receptionist", "school-workers",
        "Who welcomes visitors at the school entrance and answers the phone?",
        (HEADMASTER, RECEPTIONIST, COOK), "receptionist",
        "The receptionist welcomes visitors and answers calls at reception.",
    ),
    Item(
        "worker-librarian", "school-workers",
        "Who organises the school library books and helps you borrow them?",
        (CARETAKER, TEACHER, LIBRARIAN), "librarian",
        "The librarian looks after library books and helps people find and borrow them.",
    ),
    Item(
        "family-mum", "family",
        "A woman has a baby daughter. What is the woman to the baby?",
        (MUM, SISTER, AUNT), "mum",
        "She is the baby's mum, or mother.", "family",
    ),
    Item(
        "family-dad", "family",
        "A man has a son. What is the man to his son?",
        (UNCLE, DAD, BROTHER), "dad",
        "He is his son's dad, or father.", "family",
    ),
    Item(
        "family-sister", "family",
        "Your parents have another daughter. Who is she to you?",
        (COUSIN, AUNT, SISTER), "sister",
        "Another daughter of your parents is your sister.", "family",
    ),
    Item(
        "family-brother", "family",
        "Your parents have another son. Who is he to you?",
        (BROTHER, UNCLE, GRANDPA), "brother",
        "Another son of your parents is your brother.", "family",
    ),
    Item(
        "family-grandma", "family",
        "Who is your mum's mother?",
        (AUNT, GRANDMA, SISTER), "grandma",
        "Your mum's mother is your grandma, or grandmother.", "family",
    ),
    Item(
        "family-grandpa", "family",
        "Who is your dad's father?",
        (BROTHER, UNCLE, GRANDPA), "grandpa",
        "Your dad's father is your grandpa, or grandfather.", "family",
    ),
    Item(
        "family-baby", "family",
        "What do we call a child who has just been born?",
        (BABY, GRANDPA, PET), "baby",
        "A child who has just been born is a baby.", "family",
    ),
    Item(
        "family-aunt", "family",
        "Your dad has a sister. Who is she to you?",
        (SISTER, AUNT, GRANDMA), "aunt",
        "A sister of your mum or dad is your aunt.", "family",
    ),
    Item(
        "family-uncle", "family",
        "Your mum has a brother. Who is he to you?",
        (DAD, COUSIN, UNCLE), "uncle",
        "A brother of your mum or dad is your uncle.", "family",
    ),
    Item(
        "family-cousin", "family",
        "Your aunt has a child. Who is that child to you?",
        (COUSIN, BROTHER, UNCLE), "cousin",
        "Your aunt's or uncle's child is your cousin.", "family",
    ),
    Item(
        "family-pet", "family",
        "A dog lives with a family and they care for it. What is it to the family?",
        (BABY, PET, COUSIN), "pet",
        "An animal that a family keeps and cares for is a pet.", "family",
    ),
    Item(
        "settlement-neighbourhood", "settlements",
        "What is the local area around your home called?",
        (CITY, VILLAGE, NEIGHBOURHOOD), "neighbourhood",
        "Your neighbourhood is the local area around your home.",
    ),
    Item(
        "settlement-village", "settlements",
        "Which is usually the smallest settlement, with fewer people and buildings?",
        (VILLAGE, TOWN, CITY), "village",
        "A village is usually smaller than a town or a city.",
    ),
    Item(
        "settlement-town", "settlements",
        "Which settlement is usually bigger than a village but smaller than a city?",
        (CITY, TOWN, VILLAGE), "town",
        "A town is usually larger than a village and smaller than a city.",
    ),
    Item(
        "settlement-city", "settlements",
        "Which settlement usually has the most people, buildings and busy streets?",
        (TOWN, VILLAGE, CITY), "city",
        "A city is usually larger and busier than a town or a village.",
    ),
    Item(
        "helper-mayor", "community-helpers",
        "Who heads the local council?",
        (MAYOR, POLICE_OFFICER, DOCTOR), "mayor",
        "The mayor heads the local council.",
    ),
    Item(
        "helper-doctor", "community-helpers",
        "You feel ill. Who examines you at the health centre?",
        (FIREFIGHTER, DOCTOR, GARDENER), "doctor",
        "A doctor examines people who are ill and helps treat their illnesses.",
    ),
    Item(
        "helper-gardener", "community-helpers",
        "Who plants flowers and looks after the plants in a public park?",
        (STREET_CLEANER, POSTMAN, GARDENER), "gardener",
        "A gardener plants and cares for flowers, trees and other plants.",
    ),
    Item(
        "helper-firefighter", "community-helpers",
        "There is a fire in a building. Whose job is to put it out?",
        (FIREFIGHTER, POLICE_OFFICER, BUS_DRIVER), "firefighter",
        "Firefighters put out fires and help rescue people.",
    ),
    Item(
        "helper-police-officer", "community-helpers",
        "Someone has stolen a bicycle. Who investigates crimes and helps keep people safe?",
        (MAYOR, POLICE_OFFICER, POSTMAN), "police-officer",
        "A police officer investigates crimes and helps keep the community safe.",
    ),
    Item(
        "helper-bus-driver", "community-helpers",
        "Who drives a bus to take passengers from one stop to the next?",
        (POSTMAN, DOCTOR, BUS_DRIVER), "bus-driver",
        "A bus driver takes passengers along a bus route.",
    ),
    Item(
        "helper-postman", "community-helpers",
        "A letter is on its way to your home. Who delivers it?",
        (POSTMAN, STREET_CLEANER, MAYOR), "postman",
        "The postman delivers letters to homes and other buildings.",
    ),
    Item(
        "helper-street-cleaner", "community-helpers",
        "There is litter on the pavement. Who sweeps it up?",
        (GARDENER, STREET_CLEANER, FIREFIGHTER), "street-cleaner",
        "Street cleaners sweep streets and remove litter to keep public places clean.",
    ),
    Item(
        "community-helpers-concept", "community",
        "What do we call people whose jobs help people in our community?",
        (
            Choice("family-members", "Family members"),
            Choice("school-places", "School places"),
            Choice("community-helpers", "Community helpers"),
        ),
        "community-helpers",
        "Community helpers do jobs that help people, such as teaching or putting out fires.",
        "neighbourhood",
    ),
    Item(
        "community-public-services", "community",
        "Street cleaning and public libraries help everyone. What are they examples of?",
        (
            Choice("public-services", "Public services"),
            Choice("family-relationships", "Family relationships"),
            Choice("settlements", "Types of settlement"),
        ),
        "public-services",
        "Public services provide help and facilities for people in the community.",
        "neighbourhood",
    ),
    Item(
        "community-local-council", "community",
        "Which group organises public services, such as cleaning streets?",
        (
            Choice("school-staff", "The school staff"),
            Choice("local-council", "The local council"),
            Choice("one-family", "One family"),
        ),
        "local-council",
        "The local council organises local public services. The mayor heads the council.",
        "neighbourhood",
    ),
)

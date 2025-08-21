import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
connection = sqlite3.connect('devops_management.db')
connection.execute("PRAGMA foreign_keys = ON;")
cursor = connection.cursor()

#settings
NUM_USERS = 3000
NUM_ENVIRONMENTS = 2000
NUM_CONFIGS = 2000
NUM_CATEGORIES = 10
NUM_SOURCE_CTRL = 20
NUM_TESTING = 20
NUM_SERVICES = 50
NUM_PIPELINES = 50
NUM_STEPS = 5
NUM_DEPLOYMENTS = 50000
NUM_LOGS = 200000
NUM_USES = 1000
NUM_ACCESSES = 1000

#auto commit disable for performance??
#connection.execute('PRAGMA synchronous = OFF')
#connection.execute('PRAGMA journal_mode = MEMORY')

print('beginning database seeding')

# Tool Categories - Must be inserted first as other tables reference it
tool_categories = [(f"{fake.word().title()} Tools",) for _ in range(NUM_CATEGORIES)]
cursor.executemany("INSERT INTO Tool_Category (category_name) VALUES (?)", tool_categories)

# Users - Must be inserted before Config_File, Deployment, Uses, Accesses
users = [(fake.name(), fake.unique.email(), fake.job()) for _ in range(NUM_USERS)]
cursor.executemany("INSERT INTO User (name, email, role) VALUES (?, ?, ?)", users)

# Config Files - Must be inserted before Environment
config_files = [
    (fake.file_name(extension="yaml"), fake.sha1(), random.randint(1, NUM_USERS))
    for _ in range(NUM_CONFIGS)
]
cursor.executemany("INSERT INTO Config_File (name, hash, user_id) VALUES (?, ?, ?)", config_files)

# Environments - Must be inserted before Deployment and Uses
environments = [
    (fake.domain_word(), random.choice([0, 1]), random.randint(1, NUM_CONFIGS))
    for _ in range(NUM_ENVIRONMENTS)
]
cursor.executemany("INSERT INTO Environment (name, is_active, file_id) VALUES (?, ?, ?)", environments)

# Source Control Tools
source_ctrl = [
    (fake.domain_word(), "Git-based", f"{random.randint(1, 5)}.{random.randint(0, 9)}", random.randint(1, NUM_CATEGORIES))
    for _ in range(NUM_SOURCE_CTRL)
]
cursor.executemany("INSERT INTO Source_Ctrl (name, type, version, category_id) VALUES (?, ?, ?, ?)", source_ctrl)

# Testing Tools
testing_tools = [
    (fake.domain_word(), "CI/CD", f"{random.randint(1, 5)}.{random.randint(0, 9)}", random.randint(1, NUM_CATEGORIES))
    for _ in range(NUM_TESTING)
]
cursor.executemany("INSERT INTO Testing (name, type, version, category_id) VALUES (?, ?, ?, ?)", testing_tools)

# Services - Must be inserted before Pipeline, Deployment, Accesses
services = [(fake.domain_word(), random.choice([0, 1])) for _ in range(NUM_SERVICES)]
cursor.executemany("INSERT INTO Service (name, is_active) VALUES (?, ?)", services)

# Pipelines - Must be inserted before Pipeline_Step
pipelines = [(fake.bs(), random.randint(1, NUM_SERVICES)) for _ in range(NUM_PIPELINES)]
cursor.executemany("INSERT INTO Pipeline (name, service_id) VALUES (?, ?)", pipelines)

# Pipeline Steps
pipeline_steps = []
for pipe_id in range(1, NUM_PIPELINES + 1):
    for step_id in range(1, NUM_STEPS + 1):
        pipeline_steps.append((pipe_id, step_id, fake.bs()))
cursor.executemany("INSERT INTO Pipeline_Step (pipe_id, step_id, name) VALUES (?, ?, ?)", pipeline_steps)

# Deployments
deployments = []
for _ in range(NUM_DEPLOYMENTS):
    deployments.append((
        random.choice(["SUCCESS", "FAILURE", "PENDING"]),
        f"{random.randint(1, 10)}.{random.randint(0, 9)}",
        fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
        random.randint(1, NUM_USERS),
        random.randint(1, NUM_ENVIRONMENTS),
        random.randint(1, NUM_SERVICES)
    ))
cursor.executemany("INSERT INTO Deployment (status, version, timestamp, user_id, env_id, service_id) VALUES (?, ?, ?, ?, ?, ?)", deployments)

# Logs
logs = []
for _ in range(NUM_LOGS):
    logs.append((
        random.choice(["INFO", "WARNING", "ERROR"]),
        fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
        random.randint(1, NUM_DEPLOYMENTS)
    ))
cursor.executemany("INSERT INTO Log (type, timestamp, deploy_id) VALUES (?, ?, ?)", logs)

# Uses
uses = set()
while len(uses) < NUM_USES:
    uses.add((random.randint(1, NUM_USERS), random.randint(1, NUM_CATEGORIES), random.randint(1, NUM_ENVIRONMENTS)))
cursor.executemany("INSERT INTO Uses (user_id, category_id, env_id) VALUES (?, ?, ?)", list(uses))

# Accesses
accesses = {}
while len(accesses) < NUM_ACCESSES:
    user_id = random.randint(1, NUM_USERS)
    service_id = random.randint(1, NUM_SERVICES)
    key = (user_id, service_id)
    if key not in accesses:
        permission = random.choice(["READ", "write", "admin", "execute", "read-write"])
        accesses[key] = permission
cursor.executemany(
    "INSERT INTO Accesses (user_id, service_id, permissions) VALUES (?, ?, ?)",
    [(u, s, p) for (u, s), p in accesses.items()]
)

# Commit and close connections
connection.commit()
connection.close()

print('database seeding complete')
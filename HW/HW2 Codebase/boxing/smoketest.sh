#!/bin/bash

# Base URL for the Flask API
BASE_URL="http://localhost:5000/api"
ECHO_JSON=false

# Parse command-line flags
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Pretty print JSON if flag is set
print_json() {
  if [ "$ECHO_JSON" = true ]; then
    echo "$1" | jq .
  fi
}

# ------------------------------
# Health Checks
# ------------------------------

check_health() {
  """
  Checks the service health endpoint.
  Exits with an error if the health check fails.
  """
  echo "Checking service health..."
  response=$(curl -s "$BASE_URL/health")
  echo "$response" | grep -q '"status": "success"' || { echo "Health check failed."; exit 1; }
  echo "Service is healthy."
}

check_db() {
  """
  Checks the database connection endpoint.
  Exits with an error if the database check fails.
  """
  echo "Checking database connection..."
  response=$(curl -s "$BASE_URL/db-check")
  echo "$response" | grep -q '"status": "success"' || { echo "Database check failed."; exit 1; }
  echo "Database connection is healthy."
}

# ------------------------------
# Boxer Management
# ------------------------------

create_boxer() {
  """
  Creates a boxer using the provided name, weight, height, reach, and age.
  Exits with an error if the boxer creation fails.
  Prints the JSON response if ECHO_JSON is set.
  """
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer: $name..."
  response=$(curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}")

  echo "$response" | grep -q '"status": "success"' || { echo "Failed to create boxer $name."; exit 1; }
  echo "Boxer $name added."
  print_json "$response"
}

get_boxer_by_name() {
  """
  Retrieves a boxer by their name.
  Exits with an error if the retrieval fails.
  Prints the JSON response if ECHO_JSON is set.
  """
  name=$1
  echo "Getting boxer by name: $name..."
  response=$(curl -s "$BASE_URL/get-boxer-by-name/$name")
  echo "$response" | grep -q '"status": "success"' || { echo "Failed to get boxer $name."; exit 1; }
  print_json "$response"
}

get_boxer_by_id() {
  """
  Retrieves a boxer by their ID.
  Exits with an error if the retrieval fails.
  Prints the JSON response if ECHO_JSON is set.
  """
  id=$1
  echo "Getting boxer by ID: $id..."
  response=$(curl -s "$BASE_URL/get-boxer-by-id/$id")
  echo "$response" | grep -q '"status": "success"' || { echo "Failed to get boxer ID $id."; exit 1; }
  print_json "$response"
}

# ------------------------------
# Ring Management
# ------------------------------

enter_ring() {
  """
  Enters a boxer into the ring by their name.
  Exits with an error if the boxer fails to enter the ring.
  Prints the JSON response if ECHO_JSON is set.
  """
  name=$1
  echo "Entering $name into the ring..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}")
  echo "$response" | grep -q '"status": "success"' || { echo "Failed to enter $name into the ring."; exit 1; }
  print_json "$response"
}

trigger_fight() {
  """
  Triggers a fight between boxers in the ring.
  Exits with an error if the fight fails.
  Prints the JSON response if ECHO_JSON is set.
  """
  echo "Triggering a fight..."
  response=$(curl -s "$BASE_URL/fight")
  echo "$response" | grep -q '"status": "success"' || { echo "Fight failed."; exit 1; }
  echo "Fight complete. Winner:"
  print_json "$response"
}

clear_ring() {
  """
  Clears all boxers from the ring.
  Exits with an error if clearing the ring fails.
  """
  echo "Clearing the ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")
  echo "$response" | grep -q '"status": "success"' || { echo "Failed to clear ring."; exit 1; }
  echo "Ring cleared."
}

get_ring_state() {
  """
  Retrieves the current state of the ring (boxers in the ring).
  Exits with an error if retrieving the ring state fails.
  Prints the JSON response if ECHO_JSON is set.
  """
  echo "Getting current boxers in ring..."
  response=$(curl -s "$BASE_URL/get-boxers")
  echo "$response" | grep -q '"status": "success"' || { echo "Failed to get ring state."; exit 1; }
  print_json "$response"
}

# ------------------------------
# Leaderboard
# ------------------------------

get_leaderboard() {
  """
  Retrieves the leaderboard, sorted by the specified criteria (wins or win_pct).
  Exits with an error if retrieving the leaderboard fails.
  Prints the JSON response if ECHO_JSON is set.
  """
  sort=$1
  echo "Getting leaderboard sorted by $sort..."
  response=$(curl -s "$BASE_URL/leaderboard?sort=$sort")
  echo "$response" | grep -q '"status": "success"' || { echo "Failed to get leaderboard."; exit 1; }
  print_json "$response"
}

# ------------------------------
# Run Tests
# ------------------------------

check_health
check_db

create_boxer "Rocky Balboa" 190 180 74.5 30
create_boxer "Ivan Drago" 210 185 78 29

# Extract dynamic boxer IDs
rocky_id=$(curl -s "$BASE_URL/get-boxer-by-name/Rocky%20Balboa" | jq '.boxer.id')
drago_id=$(curl -s "$BASE_URL/get-boxer-by-name/Ivan%20Drago" | jq '.boxer.id')

get_boxer_by_id "$rocky_id"
get_boxer_by_id "$drago_id"

enter_ring "Rocky Balboa"
enter_ring "Ivan Drago"
get_ring_state

trigger_fight
get_leaderboard wins
get_leaderboard win_pct

clear_ring
get_ring_state

# Optional cleanup
# Uncomment if DELETE route exists
# echo "Deleting test boxers..."
# curl -s -X DELETE "$BASE_URL/delete-boxer/$rocky_id"
# curl -s -X DELETE "$BASE_URL/delete-boxer/$drago_id"

echo "All smoketests passed successfully."
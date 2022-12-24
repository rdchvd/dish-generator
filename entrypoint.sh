if [ "$TARGET" == "test" ]; then
    echo "Running tests..."
    python -m tests.run_tests
    echo "Creating test report..."
    coverage run -m tests.run_tests && coverage html


  else
    echo "Running migrations..."
    alembic upgrade head
    echo "Running server..."
    uvicorn handler:app --reload --port "8000" --host 0.0.0.0
fi

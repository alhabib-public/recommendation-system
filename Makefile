run-service:
	docker build -t recommendation-api .
	docker run -p 8000:8000 -v .:/shared/ --memory=16g --memory-swap=16g  recommendation-api

# Run Tests Locally after running the service with make run-service
test-endpoint:
	python -m pytest -vv tests/test_recommendation.py

stress-test:
	locust -f tests/stress_test.py --host=http://localhost:8000
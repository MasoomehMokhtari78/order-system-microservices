# Dockerfile for tests
FROM python:3.11

WORKDIR /tests

COPY requirements-tests.txt .
RUN pip install -r requirements-tests.txt
RUN pip install pytest-xdist

COPY test_e2e.py .

CMD ["ptw", "--onfail", "echo 'Tests failed!'"]

FROM python:3.12-slim-bookworm
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
ENV PATH /code/.local/bin:${PATH}
ENV PYTHONPATH=/code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY CustomAPI /code/CustomAPI
COPY Routers /code/Routers
COPY customapi.py /code/customapi.py
CMD ["uvicorn", "customapi:app", "--host", "0.0.0.0", "--port", "8080"]
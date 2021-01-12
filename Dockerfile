FROM python:3
ADD space_trucking /space_trucking
ADD requirements.txt /
RUN pip install -r requirements.txt
EXPOSE 80


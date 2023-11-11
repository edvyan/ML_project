FROM akraradets/ait-ml-base:2023

# Set the working directory in the container
WORKDIR /app

RUN pip3 install dash
RUN pip3 install dash_bootstrap_components
RUN pip3 install pandas
RUN pip3 install numpy
RUN pip3 install scikit-learn
RUN pip3 install joblib

COPY . /app


EXPOSE 8050

ENV NAME World

CMD tail -f /dev/null
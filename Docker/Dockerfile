FROM ubuntu:kinetic

RUN apt update -y && apt install -y \
	git \
	cmake \
	build-essential
	
RUN mkdir -p /src
WORKDIR /src

ADD ./ /src
RUN mkdir build

WORKDIR /src/build
#RUN cmake ../ && make -j32

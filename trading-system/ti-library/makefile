SRC = src/
UTILS = src/
LIB = lib/
COMPILER = g++
FLAGS = -c -Wall


stonks: $(SRC)main.cpp $(UTILS)singleStock.cpp
	g++ -o stonks $(SRC)main.cpp $(UTILS)singleStock.cpp -I.

clean:
	rm $(LIB)*.o stonks



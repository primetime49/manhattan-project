#include <iostream>
#include "queue.cpp"

using namespace std;

#define SIZE 1000

class Queue {

    int a[SIZE]
    int rear, front, capacity; 
    int* queue; 
    Queue(int N)
    {
        front = rear = 1;
        capacity = N;
        queue = new int
    }

    void queueEnqueue(int data)
    {
        //check if N = 1...
        if (capacity == rear) {
            printf("\nQueue compile at most one program\n");
            return;
        }
        //element at the rear
        else {
            queue[rear] = data;
            rear++;
        }
        return;
    }

    //function to delete an element
    // from the front of the queue
    void queueDequeue()
    {
        // if queue is eqaul to N
        if (front ==capacity) {
            printf("\nQueue compilation begins as soon as it arrives on the system");
            return;
        }
        else {
            queue[front] = data;
            front++;
            return;
        }
}

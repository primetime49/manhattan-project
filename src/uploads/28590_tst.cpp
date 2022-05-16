#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>
#include <string>
#include <float.h>
using namespace std;

#define SCREEN_HEIGHT 50
#define SCREEN_WIDTH 150

class Vertex{
   public:
   Vertex() {
      x = 0;
      y = 0;
      z = 0;
   }
   
   Vertex(double new_x, double new_y, double new_z = 0){
      x = new_x;
      y = new_y;
      z = new_z;
   }   
   
   double x;
   double y;
   double z;

   private:

};

class Shape{
   public:
   virtual double max_x() = 0;
   virtual double max_y() = 0;
   virtual double min_x() = 0;
   virtual double min_y() = 0;
   virtual void rasterize(char (&board)[SCREEN_HEIGHT+1][SCREEN_WIDTH+1], double ratio_x, double ratio_y, double min_x, double min_y, int mark) = 0;

   private:

};

class Triangle : public Shape{
   public:
   Triangle(Vertex& new_v1, Vertex& new_v2, Vertex& new_v3){
      v1 = new_v1;
      v1.x = v1.x/v1.z;
      v1.y = v1.y/v1.z;
      v2 = new_v2;
      v2.x = v2.x/v2.z;
      v2.y = v2.y/v2.z;
      v3 = new_v3;
      v3.x = v3.x/v3.z;
      v3.y = v3.y/v3.z;
   }
   Vertex v1;
   Vertex v2;
   Vertex v3;

   double max_x(){
      return std::max(std::max(v1.x,v2.x),v3.x);
   }
   double max_y(){
      return std::max(std::max(v1.y,v2.y),v3.y);
   }
   double min_x(){
      return std::min(std::min(v1.x,v2.x),v3.x);
   }
   double min_y(){
      return std::min(std::min(v1.y,v2.y),v3.y);
   }

   void rasterize(char (&board)[SCREEN_HEIGHT+1][SCREEN_WIDTH+1], double ratio_x, double ratio_y, double min_x, double min_y, int mark){
      double z;
      for (int j = 0;j < sizeof(board)/sizeof(board[0]); j++){
         double py = j*ratio_y+min_y;
         for (int i = 0;i < sizeof(board[0]); i++){
            double px = i*ratio_x+min_x;
            Vertex pt(px,py,0);
            bool inside = PointInsideV3(pt,z);
            if (inside){
               board[j][i] = (int(z*10) % 10) + 48;
            } else {
               if (board[j][i] == 0){
                  board[j][i] = '-';
               }
            }
         }
      }
   }   

   private:

   double sign (Vertex p1, Vertex p2, Vertex p3){
      return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
   }

   bool PointInside (Vertex pt){
      //cout << "aaaaaaaaa" << endl;
      double d1, d2, d3;
      bool has_neg, has_pos;

      d1 = sign(pt, v1, v2);
      d2 = sign(pt, v2, v3);
      d3 = sign(pt, v3, v1);

      has_neg = (d1 < 0) || (d2 < 0) || (d3 < 0);
      has_pos = (d1 > 0) || (d2 > 0) || (d3 > 0);

      return !(has_neg && has_pos);
   }

   double determ (Vertex p1, Vertex p2, Vertex p3){
      return abs(0.5*((p3.y-p2.y)*p1.x-(p3.x-p2.x)*p1.y+p3.x*p2.y-p2.x*p3.y));
   }

   bool zeroone (double a) {
      return (a>=0 && a<=1);
   }

   bool PointInsideV2 (Vertex pt) {
      double area1,area2,area3;
      double a1,a2,a3;

      area1 = determ(pt,v2,v3);
      area2 = determ(pt,v1,v3);
      area3 = determ(pt,v1,v2);

      a1 = area1/(area1+area2+area3);
      a2 = area2/(area1+area2+area3);
      a3 = area3/(area1+area2+area3);
      cout << a1 << " " << a2 << " " << a3 << endl;

      return (zeroone(a1) && zeroone(a2) && zeroone(a3));
   }

   bool PointInsideV3 (Vertex pt, double &z) {
      double d1, d2, d3, area;

      area = sign(v1,v2,v3);
      d1 = sign(pt, v1, v2)/area;
      d2 = sign(pt, v2, v3)/area;
      d3 = sign(pt, v3, v1)/area;

      //cout << d1 << " " << d2 << " " << d3 << endl;
      //cout << z << endl;
      z = d1*v3.z + d2*v1.z + d3*v2.z;\

      //if (d1+d2+d3 == 1) {
      //   cout << "true" << endl;
      //}

      //return (d1>=0 && d2>= 0 && d3 >= 0);
      return (zeroone(d1) && zeroone(d2) && zeroone(d3));
   }
};

class Shader{
   public:
   Shader(vector<Shape*> fragments){
      objects = fragments;
   }

   vector<Shape*> objects;

   char board[SCREEN_HEIGHT+1][SCREEN_WIDTH+1] ={0} ;

   double max_x(){
      double max = -DBL_MIN;
      for (int i = 0; i < objects.size(); i++){
         double this_max = objects[i]->max_x();
         if (this_max > max){
            max = this_max;
         }
      }
      return max;
   }
   double max_y(){
      double max = -DBL_MIN;
      for (int i = 0; i < objects.size(); i++){
         double this_max = objects[i]->max_y();
         if (this_max > max){
            max = this_max;
         }
      }
      return max;
   }
   double min_x(){
      double min = DBL_MAX;
      for (int i = 0; i < objects.size(); i++){
         double this_min = objects[i]->min_x();
         if (this_min < min){
            min = this_min;
         }
      }
      return min;
   }
   double min_y(){
      double min = DBL_MAX;
      for (int i = 0; i < objects.size(); i++){
         double this_min = objects[i]->min_y();
         if (this_min < min){
            min = this_min;
         }
      }
      return min;
   }

   double ratio_x(){
      return (max_x()-min_x())/SCREEN_WIDTH;
   }

   double ratio_y(){
      return (max_y()-min_y())/SCREEN_HEIGHT;
   }

   double adjusted_ratio(){
      return std::max(ratio_x(), ratio_y());
   }

   void draw(){
      for (int ii = 0; ii < objects.size(); ii++){
         
         objects[ii]->rasterize(board, ratio_x(), ratio_y(), min_x(), min_y(), ii);
      }

      ofstream myfile ("example.txt");
      if (myfile.is_open()){
         for (int j = 0;j < sizeof(board)/sizeof(board[0]); j++){
            for (int i = 0;i < sizeof(board[0]); i++){
               myfile << board[j][i];
            }
            myfile << "" << endl;
         }
      }
      myfile.close();
   }

   private:


};

// main() is where program execution begins.
int main() {
   cout << "Hello World" << endl; // prints Hello World
   /*Vertex v1(0, 10, 1.5);
   Vertex v2(50,8, 1.1);
   Vertex v3(25, 0, 1.5);
   Vertex v4(30, 15, 1.9);
   Vertex v5(45,13.5,1);*/
   Vertex v1(1, -1, 1.5);
   Vertex v2(1,1, 1.1);
   Vertex v3(-1, 1, 1.5);
   Vertex v4(-1, -1, 1.9);
   //cout << v1.x << endl;

   Triangle t1(v1,v2,v3);
   Triangle t2(v1,v3,v4);
   //Triangle t3(v3,v1,v5);
   vector<Shape*> fragments;
   fragments.push_back(&t1);
   fragments.push_back(&t2);
   //fragments.push_back(&t3);

   Shader shader(fragments);
   shader.draw();

   cout << shader.max_x() << endl;
   cout << shader.min_x() << endl;
   cout << shader.max_y() << endl;
   cout << shader.min_y() << endl;
   return 0;
}
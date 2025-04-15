

#include <iostream>
#include <numeric>
#include <vector>
using namespace std;

int main() {
    vector<int> nums(100);
    iota(nums.begin(), nums.end(), 1); // 填充1-100
    
    int sum = accumulate(nums.begin(), nums.end(), 0);
    cout << "STL计算结果: " << sum << endl;
    return 0;
}

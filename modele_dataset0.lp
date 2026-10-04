\ Model learn_mrsort
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  error[0] + error[1] + error[2] + error[3] + error[4] + error[5] + error[6]
   + error[7] + error[8] + error[9] + error[10] + error[11] + error[12]
   + error[13] + error[14] + error[15] + error[16] + error[17] + error[18]
   + error[19] + error[20] + error[21] + error[22] + error[23] + error[24]
   + error[25] + error[26] + error[27] + error[28] + error[29] + error[30]
   + error[31] + error[32] + error[33] + error[34] + error[35] + error[36]
   + error[37] + error[38] + error[39] + error[40] + error[41] + error[42]
   + error[43] + error[44] + error[45] + error[46] + error[47] + error[48]
   + error[49] + error[50] + error[51] + error[52] + error[53] + error[54]
   + error[55] + error[56] + error[57] + error[58] + error[59]
Subject To
 normalize_weights: w[0] + w[1] + w[2] + w[3] + w[4] = 1
 ordered_boundary[0,0]: b[0,0] - b[1,0] <= 0
 ordered_boundary[0,1]: b[0,1] - b[1,1] <= 0
 ordered_boundary[0,2]: b[0,2] - b[1,2] <= 0
 ordered_boundary[0,3]: b[0,3] - b[1,3] <= 0
 ordered_boundary[0,4]: b[0,4] - b[1,4] <= 0
 criterion_pass[0]: b[0,0] + 100.0001 delta[0,0,3.0] <= 103.0001
 criterion_fail[0]: b[0,0] + 100.0001 delta[0,0,3.0] >= 3.0001
 contribution_weight[0]: - w[0] + contribution[0,0,3.0] <= 0
 contribution_indicator[0]: - delta[0,0,3.0] + contribution[0,0,3.0] <= 0
 contribution_lower[0]: - w[0] - delta[0,0,3.0] + contribution[0,0,3.0]
   >= -1
 criterion_pass[1]: b[0,0] + 100.0001 delta[0,0,5.0] <= 105.0001
 criterion_fail[1]: b[0,0] + 100.0001 delta[0,0,5.0] >= 5.0001
 contribution_weight[1]: - w[0] + contribution[0,0,5.0] <= 0
 contribution_indicator[1]: - delta[0,0,5.0] + contribution[0,0,5.0] <= 0
 contribution_lower[1]: - w[0] - delta[0,0,5.0] + contribution[0,0,5.0]
   >= -1
 criterion_pass[2]: b[0,0] + 100.0001 delta[0,0,10.0] <= 110.0001
 criterion_fail[2]: b[0,0] + 100.0001 delta[0,0,10.0] >= 10.0001
 contribution_weight[2]: - w[0] + contribution[0,0,10.0] <= 0
 contribution_indicator[2]: - delta[0,0,10.0] + contribution[0,0,10.0]
   <= 0
 contribution_lower[2]: - w[0] - delta[0,0,10.0] + contribution[0,0,10.0]
   >= -1
 criterion_pass[3]: b[0,0] + 100.0001 delta[0,0,11.0] <= 111.0001
 criterion_fail[3]: b[0,0] + 100.0001 delta[0,0,11.0] >= 11.0001
 contribution_weight[3]: - w[0] + contribution[0,0,11.0] <= 0
 contribution_indicator[3]: - delta[0,0,11.0] + contribution[0,0,11.0]
   <= 0
 contribution_lower[3]: - w[0] - delta[0,0,11.0] + contribution[0,0,11.0]
   >= -1
 criterion_pass[4]: b[0,0] + 100.0001 delta[0,0,19.0] <= 119.0001
 criterion_fail[4]: b[0,0] + 100.0001 delta[0,0,19.0] >= 19.0001
 contribution_weight[4]: - w[0] + contribution[0,0,19.0] <= 0
 contribution_indicator[4]: - delta[0,0,19.0] + contribution[0,0,19.0]
   <= 0
 contribution_lower[4]: - w[0] - delta[0,0,19.0] + contribution[0,0,19.0]
   >= -1
 criterion_pass[5]: b[0,0] + 100.0001 delta[0,0,20.0] <= 120.0001
 criterion_fail[5]: b[0,0] + 100.0001 delta[0,0,20.0] >= 20.0001
 contribution_weight[5]: - w[0] + contribution[0,0,20.0] <= 0
 contribution_indicator[5]: - delta[0,0,20.0] + contribution[0,0,20.0]
   <= 0
 contribution_lower[5]: - w[0] - delta[0,0,20.0] + contribution[0,0,20.0]
   >= -1
 criterion_pass[6]: b[0,0] + 100.0001 delta[0,0,22.0] <= 122.0001
 criterion_fail[6]: b[0,0] + 100.0001 delta[0,0,22.0] >= 22.0001
 contribution_weight[6]: - w[0] + contribution[0,0,22.0] <= 0
 contribution_indicator[6]: - delta[0,0,22.0] + contribution[0,0,22.0]
   <= 0
 contribution_lower[6]: - w[0] - delta[0,0,22.0] + contribution[0,0,22.0]
   >= -1
 criterion_pass[7]: b[0,0] + 100.0001 delta[0,0,25.0] <= 125.0001
 criterion_fail[7]: b[0,0] + 100.0001 delta[0,0,25.0] >= 25.0001
 contribution_weight[7]: - w[0] + contribution[0,0,25.0] <= 0
 contribution_indicator[7]: - delta[0,0,25.0] + contribution[0,0,25.0]
   <= 0
 contribution_lower[7]: - w[0] - delta[0,0,25.0] + contribution[0,0,25.0]
   >= -1
 criterion_pass[8]: b[0,0] + 100.0001 delta[0,0,26.0] <= 126.0001
 criterion_fail[8]: b[0,0] + 100.0001 delta[0,0,26.0] >= 26.0001
 contribution_weight[8]: - w[0] + contribution[0,0,26.0] <= 0
 contribution_indicator[8]: - delta[0,0,26.0] + contribution[0,0,26.0]
   <= 0
 contribution_lower[8]: - w[0] - delta[0,0,26.0] + contribution[0,0,26.0]
   >= -1
 criterion_pass[9]: b[0,0] + 100.0001 delta[0,0,30.0] <= 130.0001
 criterion_fail[9]: b[0,0] + 100.0001 delta[0,0,30.0] >= 30.0001
 contribution_weight[9]: - w[0] + contribution[0,0,30.0] <= 0
 contribution_indicator[9]: - delta[0,0,30.0] + contribution[0,0,30.0]
   <= 0
 contribution_lower[9]: - w[0] - delta[0,0,30.0] + contribution[0,0,30.0]
   >= -1
 criterion_pass[10]: b[0,0] + 100.0001 delta[0,0,32.0] <= 132.0001
 criterion_fail[10]: b[0,0] + 100.0001 delta[0,0,32.0] >= 32.0001
 contribution_weight[10]: - w[0] + contribution[0,0,32.0] <= 0
 contribution_indicator[10]: - delta[0,0,32.0] + contribution[0,0,32.0]
   <= 0
 contribution_lower[10]: - w[0] - delta[0,0,32.0] + contribution[0,0,32.0]
   >= -1
 criterion_pass[11]: b[0,0] + 100.0001 delta[0,0,33.0] <= 133.0001
 criterion_fail[11]: b[0,0] + 100.0001 delta[0,0,33.0] >= 33.0001
 contribution_weight[11]: - w[0] + contribution[0,0,33.0] <= 0
 contribution_indicator[11]: - delta[0,0,33.0] + contribution[0,0,33.0]
   <= 0
 contribution_lower[11]: - w[0] - delta[0,0,33.0] + contribution[0,0,33.0]
   >= -1
 criterion_pass[12]: b[0,0] + 100.0001 delta[0,0,37.0] <= 137.0001
 criterion_fail[12]: b[0,0] + 100.0001 delta[0,0,37.0] >= 37.0001
 contribution_weight[12]: - w[0] + contribution[0,0,37.0] <= 0
 contribution_indicator[12]: - delta[0,0,37.0] + contribution[0,0,37.0]
   <= 0
 contribution_lower[12]: - w[0] - delta[0,0,37.0] + contribution[0,0,37.0]
   >= -1
 criterion_pass[13]: b[0,0] + 100.0001 delta[0,0,38.0] <= 138.0001
 criterion_fail[13]: b[0,0] + 100.0001 delta[0,0,38.0] >= 38.0001
 contribution_weight[13]: - w[0] + contribution[0,0,38.0] <= 0
 contribution_indicator[13]: - delta[0,0,38.0] + contribution[0,0,38.0]
   <= 0
 contribution_lower[13]: - w[0] - delta[0,0,38.0] + contribution[0,0,38.0]
   >= -1
 criterion_pass[14]: b[0,0] + 100.0001 delta[0,0,40.0] <= 140.0001
 criterion_fail[14]: b[0,0] + 100.0001 delta[0,0,40.0] >= 40.0001
 contribution_weight[14]: - w[0] + contribution[0,0,40.0] <= 0
 contribution_indicator[14]: - delta[0,0,40.0] + contribution[0,0,40.0]
   <= 0
 contribution_lower[14]: - w[0] - delta[0,0,40.0] + contribution[0,0,40.0]
   >= -1
 criterion_pass[15]: b[0,0] + 100.0001 delta[0,0,42.0] <= 142.0001
 criterion_fail[15]: b[0,0] + 100.0001 delta[0,0,42.0] >= 42.0001
 contribution_weight[15]: - w[0] + contribution[0,0,42.0] <= 0
 contribution_indicator[15]: - delta[0,0,42.0] + contribution[0,0,42.0]
   <= 0
 contribution_lower[15]: - w[0] - delta[0,0,42.0] + contribution[0,0,42.0]
   >= -1
 criterion_pass[16]: b[0,0] + 100.0001 delta[0,0,45.0] <= 145.0001
 criterion_fail[16]: b[0,0] + 100.0001 delta[0,0,45.0] >= 45.0001
 contribution_weight[16]: - w[0] + contribution[0,0,45.0] <= 0
 contribution_indicator[16]: - delta[0,0,45.0] + contribution[0,0,45.0]
   <= 0
 contribution_lower[16]: - w[0] - delta[0,0,45.0] + contribution[0,0,45.0]
   >= -1
 criterion_pass[17]: b[0,0] + 100.0001 delta[0,0,46.0] <= 146.0001
 criterion_fail[17]: b[0,0] + 100.0001 delta[0,0,46.0] >= 46.0001
 contribution_weight[17]: - w[0] + contribution[0,0,46.0] <= 0
 contribution_indicator[17]: - delta[0,0,46.0] + contribution[0,0,46.0]
   <= 0
 contribution_lower[17]: - w[0] - delta[0,0,46.0] + contribution[0,0,46.0]
   >= -1
 criterion_pass[18]: b[0,0] + 100.0001 delta[0,0,47.0] <= 147.0001
 criterion_fail[18]: b[0,0] + 100.0001 delta[0,0,47.0] >= 47.0001
 contribution_weight[18]: - w[0] + contribution[0,0,47.0] <= 0
 contribution_indicator[18]: - delta[0,0,47.0] + contribution[0,0,47.0]
   <= 0
 contribution_lower[18]: - w[0] - delta[0,0,47.0] + contribution[0,0,47.0]
   >= -1
 criterion_pass[19]: b[0,0] + 100.0001 delta[0,0,49.0] <= 149.0001
 criterion_fail[19]: b[0,0] + 100.0001 delta[0,0,49.0] >= 49.0001
 contribution_weight[19]: - w[0] + contribution[0,0,49.0] <= 0
 contribution_indicator[19]: - delta[0,0,49.0] + contribution[0,0,49.0]
   <= 0
 contribution_lower[19]: - w[0] - delta[0,0,49.0] + contribution[0,0,49.0]
   >= -1
 criterion_pass[20]: b[0,0] + 100.0001 delta[0,0,56.0] <= 156.0001
 criterion_fail[20]: b[0,0] + 100.0001 delta[0,0,56.0] >= 56.0001
 contribution_weight[20]: - w[0] + contribution[0,0,56.0] <= 0
 contribution_indicator[20]: - delta[0,0,56.0] + contribution[0,0,56.0]
   <= 0
 contribution_lower[20]: - w[0] - delta[0,0,56.0] + contribution[0,0,56.0]
   >= -1
 criterion_pass[21]: b[0,0] + 100.0001 delta[0,0,59.0] <= 159.0001
 criterion_fail[21]: b[0,0] + 100.0001 delta[0,0,59.0] >= 59.0001
 contribution_weight[21]: - w[0] + contribution[0,0,59.0] <= 0
 contribution_indicator[21]: - delta[0,0,59.0] + contribution[0,0,59.0]
   <= 0
 contribution_lower[21]: - w[0] - delta[0,0,59.0] + contribution[0,0,59.0]
   >= -1
 criterion_pass[22]: b[0,0] + 100.0001 delta[0,0,60.0] <= 160.0001
 criterion_fail[22]: b[0,0] + 100.0001 delta[0,0,60.0] >= 60.0001
 contribution_weight[22]: - w[0] + contribution[0,0,60.0] <= 0
 contribution_indicator[22]: - delta[0,0,60.0] + contribution[0,0,60.0]
   <= 0
 contribution_lower[22]: - w[0] - delta[0,0,60.0] + contribution[0,0,60.0]
   >= -1
 criterion_pass[23]: b[0,0] + 100.0001 delta[0,0,62.0] <= 162.0001
 criterion_fail[23]: b[0,0] + 100.0001 delta[0,0,62.0] >= 62.0001
 contribution_weight[23]: - w[0] + contribution[0,0,62.0] <= 0
 contribution_indicator[23]: - delta[0,0,62.0] + contribution[0,0,62.0]
   <= 0
 contribution_lower[23]: - w[0] - delta[0,0,62.0] + contribution[0,0,62.0]
   >= -1
 criterion_pass[24]: b[0,0] + 100.0001 delta[0,0,66.0] <= 166.0001
 criterion_fail[24]: b[0,0] + 100.0001 delta[0,0,66.0] >= 66.0001
 contribution_weight[24]: - w[0] + contribution[0,0,66.0] <= 0
 contribution_indicator[24]: - delta[0,0,66.0] + contribution[0,0,66.0]
   <= 0
 contribution_lower[24]: - w[0] - delta[0,0,66.0] + contribution[0,0,66.0]
   >= -1
 criterion_pass[25]: b[0,0] + 100.0001 delta[0,0,69.0] <= 169.0001
 criterion_fail[25]: b[0,0] + 100.0001 delta[0,0,69.0] >= 69.0001
 contribution_weight[25]: - w[0] + contribution[0,0,69.0] <= 0
 contribution_indicator[25]: - delta[0,0,69.0] + contribution[0,0,69.0]
   <= 0
 contribution_lower[25]: - w[0] - delta[0,0,69.0] + contribution[0,0,69.0]
   >= -1
 criterion_pass[26]: b[0,0] + 100.0001 delta[0,0,73.0] <= 173.0001
 criterion_fail[26]: b[0,0] + 100.0001 delta[0,0,73.0] >= 73.0001
 contribution_weight[26]: - w[0] + contribution[0,0,73.0] <= 0
 contribution_indicator[26]: - delta[0,0,73.0] + contribution[0,0,73.0]
   <= 0
 contribution_lower[26]: - w[0] - delta[0,0,73.0] + contribution[0,0,73.0]
   >= -1
 criterion_pass[27]: b[0,0] + 100.0001 delta[0,0,81.0] <= 181.0001
 criterion_fail[27]: b[0,0] + 100.0001 delta[0,0,81.0] >= 81.0001
 contribution_weight[27]: - w[0] + contribution[0,0,81.0] <= 0
 contribution_indicator[27]: - delta[0,0,81.0] + contribution[0,0,81.0]
   <= 0
 contribution_lower[27]: - w[0] - delta[0,0,81.0] + contribution[0,0,81.0]
   >= -1
 criterion_pass[28]: b[0,0] + 100.0001 delta[0,0,83.0] <= 183.0001
 criterion_fail[28]: b[0,0] + 100.0001 delta[0,0,83.0] >= 83.0001
 contribution_weight[28]: - w[0] + contribution[0,0,83.0] <= 0
 contribution_indicator[28]: - delta[0,0,83.0] + contribution[0,0,83.0]
   <= 0
 contribution_lower[28]: - w[0] - delta[0,0,83.0] + contribution[0,0,83.0]
   >= -1
 criterion_pass[29]: b[0,0] + 100.0001 delta[0,0,85.0] <= 185.0001
 criterion_fail[29]: b[0,0] + 100.0001 delta[0,0,85.0] >= 85.0001
 contribution_weight[29]: - w[0] + contribution[0,0,85.0] <= 0
 contribution_indicator[29]: - delta[0,0,85.0] + contribution[0,0,85.0]
   <= 0
 contribution_lower[29]: - w[0] - delta[0,0,85.0] + contribution[0,0,85.0]
   >= -1
 criterion_pass[30]: b[0,0] + 100.0001 delta[0,0,86.0] <= 186.0001
 criterion_fail[30]: b[0,0] + 100.0001 delta[0,0,86.0] >= 86.0001
 contribution_weight[30]: - w[0] + contribution[0,0,86.0] <= 0
 contribution_indicator[30]: - delta[0,0,86.0] + contribution[0,0,86.0]
   <= 0
 contribution_lower[30]: - w[0] - delta[0,0,86.0] + contribution[0,0,86.0]
   >= -1
 criterion_pass[31]: b[0,0] + 100.0001 delta[0,0,90.0] <= 190.0001
 criterion_fail[31]: b[0,0] + 100.0001 delta[0,0,90.0] >= 90.0001
 contribution_weight[31]: - w[0] + contribution[0,0,90.0] <= 0
 contribution_indicator[31]: - delta[0,0,90.0] + contribution[0,0,90.0]
   <= 0
 contribution_lower[31]: - w[0] - delta[0,0,90.0] + contribution[0,0,90.0]
   >= -1
 criterion_pass[32]: b[0,0] + 100.0001 delta[0,0,91.0] <= 191.0001
 criterion_fail[32]: b[0,0] + 100.0001 delta[0,0,91.0] >= 91.0001
 contribution_weight[32]: - w[0] + contribution[0,0,91.0] <= 0
 contribution_indicator[32]: - delta[0,0,91.0] + contribution[0,0,91.0]
   <= 0
 contribution_lower[32]: - w[0] - delta[0,0,91.0] + contribution[0,0,91.0]
   >= -1
 criterion_pass[33]: b[0,0] + 100.0001 delta[0,0,93.0] <= 193.0001
 criterion_fail[33]: b[0,0] + 100.0001 delta[0,0,93.0] >= 93.0001
 contribution_weight[33]: - w[0] + contribution[0,0,93.0] <= 0
 contribution_indicator[33]: - delta[0,0,93.0] + contribution[0,0,93.0]
   <= 0
 contribution_lower[33]: - w[0] - delta[0,0,93.0] + contribution[0,0,93.0]
   >= -1
 criterion_pass[34]: b[0,0] + 100.0001 delta[0,0,99.0] <= 199.0001
 criterion_fail[34]: b[0,0] + 100.0001 delta[0,0,99.0] >= 99.0001
 contribution_weight[34]: - w[0] + contribution[0,0,99.0] <= 0
 contribution_indicator[34]: - delta[0,0,99.0] + contribution[0,0,99.0]
   <= 0
 contribution_lower[34]: - w[0] - delta[0,0,99.0] + contribution[0,0,99.0]
   >= -1
 criterion_pass[35]: b[0,1] + 100.0001 delta[0,1,2.0] <= 102.0001
 criterion_fail[35]: b[0,1] + 100.0001 delta[0,1,2.0] >= 2.0001
 contribution_weight[35]: - w[1] + contribution[0,1,2.0] <= 0
 contribution_indicator[35]: - delta[0,1,2.0] + contribution[0,1,2.0] <= 0
 contribution_lower[35]: - w[1] - delta[0,1,2.0] + contribution[0,1,2.0]
   >= -1
 criterion_pass[36]: b[0,1] + 100.0001 delta[0,1,5.0] <= 105.0001
 criterion_fail[36]: b[0,1] + 100.0001 delta[0,1,5.0] >= 5.0001
 contribution_weight[36]: - w[1] + contribution[0,1,5.0] <= 0
 contribution_indicator[36]: - delta[0,1,5.0] + contribution[0,1,5.0] <= 0
 contribution_lower[36]: - w[1] - delta[0,1,5.0] + contribution[0,1,5.0]
   >= -1
 criterion_pass[37]: b[0,1] + 100.0001 delta[0,1,6.0] <= 106.0001
 criterion_fail[37]: b[0,1] + 100.0001 delta[0,1,6.0] >= 6.0001
 contribution_weight[37]: - w[1] + contribution[0,1,6.0] <= 0
 contribution_indicator[37]: - delta[0,1,6.0] + contribution[0,1,6.0] <= 0
 contribution_lower[37]: - w[1] - delta[0,1,6.0] + contribution[0,1,6.0]
   >= -1
 criterion_pass[38]: b[0,1] + 100.0001 delta[0,1,8.0] <= 108.0001
 criterion_fail[38]: b[0,1] + 100.0001 delta[0,1,8.0] >= 8.0001
 contribution_weight[38]: - w[1] + contribution[0,1,8.0] <= 0
 contribution_indicator[38]: - delta[0,1,8.0] + contribution[0,1,8.0] <= 0
 contribution_lower[38]: - w[1] - delta[0,1,8.0] + contribution[0,1,8.0]
   >= -1
 criterion_pass[39]: b[0,1] + 100.0001 delta[0,1,9.0] <= 109.0001
 criterion_fail[39]: b[0,1] + 100.0001 delta[0,1,9.0] >= 9.0001
 contribution_weight[39]: - w[1] + contribution[0,1,9.0] <= 0
 contribution_indicator[39]: - delta[0,1,9.0] + contribution[0,1,9.0] <= 0
 contribution_lower[39]: - w[1] - delta[0,1,9.0] + contribution[0,1,9.0]
   >= -1
 criterion_pass[40]: b[0,1] + 100.0001 delta[0,1,12.0] <= 112.0001
 criterion_fail[40]: b[0,1] + 100.0001 delta[0,1,12.0] >= 12.0001
 contribution_weight[40]: - w[1] + contribution[0,1,12.0] <= 0
 contribution_indicator[40]: - delta[0,1,12.0] + contribution[0,1,12.0]
   <= 0
 contribution_lower[40]: - w[1] - delta[0,1,12.0] + contribution[0,1,12.0]
   >= -1
 criterion_pass[41]: b[0,1] + 100.0001 delta[0,1,16.0] <= 116.0001
 criterion_fail[41]: b[0,1] + 100.0001 delta[0,1,16.0] >= 16.0001
 contribution_weight[41]: - w[1] + contribution[0,1,16.0] <= 0
 contribution_indicator[41]: - delta[0,1,16.0] + contribution[0,1,16.0]
   <= 0
 contribution_lower[41]: - w[1] - delta[0,1,16.0] + contribution[0,1,16.0]
   >= -1
 criterion_pass[42]: b[0,1] + 100.0001 delta[0,1,17.0] <= 117.0001
 criterion_fail[42]: b[0,1] + 100.0001 delta[0,1,17.0] >= 17.0001
 contribution_weight[42]: - w[1] + contribution[0,1,17.0] <= 0
 contribution_indicator[42]: - delta[0,1,17.0] + contribution[0,1,17.0]
   <= 0
 contribution_lower[42]: - w[1] - delta[0,1,17.0] + contribution[0,1,17.0]
   >= -1
 criterion_pass[43]: b[0,1] + 100.0001 delta[0,1,23.0] <= 123.0001
 criterion_fail[43]: b[0,1] + 100.0001 delta[0,1,23.0] >= 23.0001
 contribution_weight[43]: - w[1] + contribution[0,1,23.0] <= 0
 contribution_indicator[43]: - delta[0,1,23.0] + contribution[0,1,23.0]
   <= 0
 contribution_lower[43]: - w[1] - delta[0,1,23.0] + contribution[0,1,23.0]
   >= -1
 criterion_pass[44]: b[0,1] + 100.0001 delta[0,1,27.0] <= 127.0001
 criterion_fail[44]: b[0,1] + 100.0001 delta[0,1,27.0] >= 27.0001
 contribution_weight[44]: - w[1] + contribution[0,1,27.0] <= 0
 contribution_indicator[44]: - delta[0,1,27.0] + contribution[0,1,27.0]
   <= 0
 contribution_lower[44]: - w[1] - delta[0,1,27.0] + contribution[0,1,27.0]
   >= -1
 criterion_pass[45]: b[0,1] + 100.0001 delta[0,1,29.0] <= 129.0001
 criterion_fail[45]: b[0,1] + 100.0001 delta[0,1,29.0] >= 29.0001
 contribution_weight[45]: - w[1] + contribution[0,1,29.0] <= 0
 contribution_indicator[45]: - delta[0,1,29.0] + contribution[0,1,29.0]
   <= 0
 contribution_lower[45]: - w[1] - delta[0,1,29.0] + contribution[0,1,29.0]
   >= -1
 criterion_pass[46]: b[0,1] + 100.0001 delta[0,1,32.0] <= 132.0001
 criterion_fail[46]: b[0,1] + 100.0001 delta[0,1,32.0] >= 32.0001
 contribution_weight[46]: - w[1] + contribution[0,1,32.0] <= 0
 contribution_indicator[46]: - delta[0,1,32.0] + contribution[0,1,32.0]
   <= 0
 contribution_lower[46]: - w[1] - delta[0,1,32.0] + contribution[0,1,32.0]
   >= -1
 criterion_pass[47]: b[0,1] + 100.0001 delta[0,1,33.0] <= 133.0001
 criterion_fail[47]: b[0,1] + 100.0001 delta[0,1,33.0] >= 33.0001
 contribution_weight[47]: - w[1] + contribution[0,1,33.0] <= 0
 contribution_indicator[47]: - delta[0,1,33.0] + contribution[0,1,33.0]
   <= 0
 contribution_lower[47]: - w[1] - delta[0,1,33.0] + contribution[0,1,33.0]
   >= -1
 criterion_pass[48]: b[0,1] + 100.0001 delta[0,1,34.0] <= 134.0001
 criterion_fail[48]: b[0,1] + 100.0001 delta[0,1,34.0] >= 34.0001
 contribution_weight[48]: - w[1] + contribution[0,1,34.0] <= 0
 contribution_indicator[48]: - delta[0,1,34.0] + contribution[0,1,34.0]
   <= 0
 contribution_lower[48]: - w[1] - delta[0,1,34.0] + contribution[0,1,34.0]
   >= -1
 criterion_pass[49]: b[0,1] + 100.0001 delta[0,1,36.0] <= 136.0001
 criterion_fail[49]: b[0,1] + 100.0001 delta[0,1,36.0] >= 36.0001
 contribution_weight[49]: - w[1] + contribution[0,1,36.0] <= 0
 contribution_indicator[49]: - delta[0,1,36.0] + contribution[0,1,36.0]
   <= 0
 contribution_lower[49]: - w[1] - delta[0,1,36.0] + contribution[0,1,36.0]
   >= -1
 criterion_pass[50]: b[0,1] + 100.0001 delta[0,1,38.0] <= 138.0001
 criterion_fail[50]: b[0,1] + 100.0001 delta[0,1,38.0] >= 38.0001
 contribution_weight[50]: - w[1] + contribution[0,1,38.0] <= 0
 contribution_indicator[50]: - delta[0,1,38.0] + contribution[0,1,38.0]
   <= 0
 contribution_lower[50]: - w[1] - delta[0,1,38.0] + contribution[0,1,38.0]
   >= -1
 criterion_pass[51]: b[0,1] + 100.0001 delta[0,1,41.0] <= 141.0001
 criterion_fail[51]: b[0,1] + 100.0001 delta[0,1,41.0] >= 41.0001
 contribution_weight[51]: - w[1] + contribution[0,1,41.0] <= 0
 contribution_indicator[51]: - delta[0,1,41.0] + contribution[0,1,41.0]
   <= 0
 contribution_lower[51]: - w[1] - delta[0,1,41.0] + contribution[0,1,41.0]
   >= -1
 criterion_pass[52]: b[0,1] + 100.0001 delta[0,1,46.0] <= 146.0001
 criterion_fail[52]: b[0,1] + 100.0001 delta[0,1,46.0] >= 46.0001
 contribution_weight[52]: - w[1] + contribution[0,1,46.0] <= 0
 contribution_indicator[52]: - delta[0,1,46.0] + contribution[0,1,46.0]
   <= 0
 contribution_lower[52]: - w[1] - delta[0,1,46.0] + contribution[0,1,46.0]
   >= -1
 criterion_pass[53]: b[0,1] + 100.0001 delta[0,1,48.0] <= 148.0001
 criterion_fail[53]: b[0,1] + 100.0001 delta[0,1,48.0] >= 48.0001
 contribution_weight[53]: - w[1] + contribution[0,1,48.0] <= 0
 contribution_indicator[53]: - delta[0,1,48.0] + contribution[0,1,48.0]
   <= 0
 contribution_lower[53]: - w[1] - delta[0,1,48.0] + contribution[0,1,48.0]
   >= -1
 criterion_pass[54]: b[0,1] + 100.0001 delta[0,1,50.0] <= 150.0001
 criterion_fail[54]: b[0,1] + 100.0001 delta[0,1,50.0] >= 50.0001
 contribution_weight[54]: - w[1] + contribution[0,1,50.0] <= 0
 contribution_indicator[54]: - delta[0,1,50.0] + contribution[0,1,50.0]
   <= 0
 contribution_lower[54]: - w[1] - delta[0,1,50.0] + contribution[0,1,50.0]
   >= -1
 criterion_pass[55]: b[0,1] + 100.0001 delta[0,1,52.0] <= 152.0001
 criterion_fail[55]: b[0,1] + 100.0001 delta[0,1,52.0] >= 52.0001
 contribution_weight[55]: - w[1] + contribution[0,1,52.0] <= 0
 contribution_indicator[55]: - delta[0,1,52.0] + contribution[0,1,52.0]
   <= 0
 contribution_lower[55]: - w[1] - delta[0,1,52.0] + contribution[0,1,52.0]
   >= -1
 criterion_pass[56]: b[0,1] + 100.0001 delta[0,1,53.0] <= 153.0001
 criterion_fail[56]: b[0,1] + 100.0001 delta[0,1,53.0] >= 53.0001
 contribution_weight[56]: - w[1] + contribution[0,1,53.0] <= 0
 contribution_indicator[56]: - delta[0,1,53.0] + contribution[0,1,53.0]
   <= 0
 contribution_lower[56]: - w[1] - delta[0,1,53.0] + contribution[0,1,53.0]
   >= -1
 criterion_pass[57]: b[0,1] + 100.0001 delta[0,1,54.0] <= 154.0001
 criterion_fail[57]: b[0,1] + 100.0001 delta[0,1,54.0] >= 54.0001
 contribution_weight[57]: - w[1] + contribution[0,1,54.0] <= 0
 contribution_indicator[57]: - delta[0,1,54.0] + contribution[0,1,54.0]
   <= 0
 contribution_lower[57]: - w[1] - delta[0,1,54.0] + contribution[0,1,54.0]
   >= -1
 criterion_pass[58]: b[0,1] + 100.0001 delta[0,1,56.0] <= 156.0001
 criterion_fail[58]: b[0,1] + 100.0001 delta[0,1,56.0] >= 56.0001
 contribution_weight[58]: - w[1] + contribution[0,1,56.0] <= 0
 contribution_indicator[58]: - delta[0,1,56.0] + contribution[0,1,56.0]
   <= 0
 contribution_lower[58]: - w[1] - delta[0,1,56.0] + contribution[0,1,56.0]
   >= -1
 criterion_pass[59]: b[0,1] + 100.0001 delta[0,1,61.0] <= 161.0001
 criterion_fail[59]: b[0,1] + 100.0001 delta[0,1,61.0] >= 61.0001
 contribution_weight[59]: - w[1] + contribution[0,1,61.0] <= 0
 contribution_indicator[59]: - delta[0,1,61.0] + contribution[0,1,61.0]
   <= 0
 contribution_lower[59]: - w[1] - delta[0,1,61.0] + contribution[0,1,61.0]
   >= -1
 criterion_pass[60]: b[0,1] + 100.0001 delta[0,1,68.0] <= 168.0001
 criterion_fail[60]: b[0,1] + 100.0001 delta[0,1,68.0] >= 68.0001
 contribution_weight[60]: - w[1] + contribution[0,1,68.0] <= 0
 contribution_indicator[60]: - delta[0,1,68.0] + contribution[0,1,68.0]
   <= 0
 contribution_lower[60]: - w[1] - delta[0,1,68.0] + contribution[0,1,68.0]
   >= -1
 criterion_pass[61]: b[0,1] + 100.0001 delta[0,1,72.0] <= 172.0001
 criterion_fail[61]: b[0,1] + 100.0001 delta[0,1,72.0] >= 72.0001
 contribution_weight[61]: - w[1] + contribution[0,1,72.0] <= 0
 contribution_indicator[61]: - delta[0,1,72.0] + contribution[0,1,72.0]
   <= 0
 contribution_lower[61]: - w[1] - delta[0,1,72.0] + contribution[0,1,72.0]
   >= -1
 criterion_pass[62]: b[0,1] + 100.0001 delta[0,1,73.0] <= 173.0001
 criterion_fail[62]: b[0,1] + 100.0001 delta[0,1,73.0] >= 73.0001
 contribution_weight[62]: - w[1] + contribution[0,1,73.0] <= 0
 contribution_indicator[62]: - delta[0,1,73.0] + contribution[0,1,73.0]
   <= 0
 contribution_lower[62]: - w[1] - delta[0,1,73.0] + contribution[0,1,73.0]
   >= -1
 criterion_pass[63]: b[0,1] + 100.0001 delta[0,1,82.0] <= 182.0001
 criterion_fail[63]: b[0,1] + 100.0001 delta[0,1,82.0] >= 82.0001
 contribution_weight[63]: - w[1] + contribution[0,1,82.0] <= 0
 contribution_indicator[63]: - delta[0,1,82.0] + contribution[0,1,82.0]
   <= 0
 contribution_lower[63]: - w[1] - delta[0,1,82.0] + contribution[0,1,82.0]
   >= -1
 criterion_pass[64]: b[0,1] + 100.0001 delta[0,1,84.0] <= 184.0001
 criterion_fail[64]: b[0,1] + 100.0001 delta[0,1,84.0] >= 84.0001
 contribution_weight[64]: - w[1] + contribution[0,1,84.0] <= 0
 contribution_indicator[64]: - delta[0,1,84.0] + contribution[0,1,84.0]
   <= 0
 contribution_lower[64]: - w[1] - delta[0,1,84.0] + contribution[0,1,84.0]
   >= -1
 criterion_pass[65]: b[0,1] + 100.0001 delta[0,1,87.0] <= 187.0001
 criterion_fail[65]: b[0,1] + 100.0001 delta[0,1,87.0] >= 87.0001
 contribution_weight[65]: - w[1] + contribution[0,1,87.0] <= 0
 contribution_indicator[65]: - delta[0,1,87.0] + contribution[0,1,87.0]
   <= 0
 contribution_lower[65]: - w[1] - delta[0,1,87.0] + contribution[0,1,87.0]
   >= -1
 criterion_pass[66]: b[0,1] + 100.0001 delta[0,1,94.0] <= 194.0001
 criterion_fail[66]: b[0,1] + 100.0001 delta[0,1,94.0] >= 94.0001
 contribution_weight[66]: - w[1] + contribution[0,1,94.0] <= 0
 contribution_indicator[66]: - delta[0,1,94.0] + contribution[0,1,94.0]
   <= 0
 contribution_lower[66]: - w[1] - delta[0,1,94.0] + contribution[0,1,94.0]
   >= -1
 criterion_pass[67]: b[0,1] + 100.0001 delta[0,1,95.0] <= 195.0001
 criterion_fail[67]: b[0,1] + 100.0001 delta[0,1,95.0] >= 95.0001
 contribution_weight[67]: - w[1] + contribution[0,1,95.0] <= 0
 contribution_indicator[67]: - delta[0,1,95.0] + contribution[0,1,95.0]
   <= 0
 contribution_lower[67]: - w[1] - delta[0,1,95.0] + contribution[0,1,95.0]
   >= -1
 criterion_pass[68]: b[0,1] + 100.0001 delta[0,1,100.0] <= 200.0001
 criterion_fail[68]: b[0,1] + 100.0001 delta[0,1,100.0] >= 100.0001
 contribution_weight[68]: - w[1] + contribution[0,1,100.0] <= 0
 contribution_indicator[68]: - delta[0,1,100.0] + contribution[0,1,100.0]
   <= 0
 contribution_lower[68]: - w[1] - delta[0,1,100.0]
   + contribution[0,1,100.0] >= -1
 criterion_pass[69]: b[0,2] + 100.0001 delta[0,2,3.0] <= 103.0001
 criterion_fail[69]: b[0,2] + 100.0001 delta[0,2,3.0] >= 3.0001
 contribution_weight[69]: - w[2] + contribution[0,2,3.0] <= 0
 contribution_indicator[69]: - delta[0,2,3.0] + contribution[0,2,3.0] <= 0
 contribution_lower[69]: - w[2] - delta[0,2,3.0] + contribution[0,2,3.0]
   >= -1
 criterion_pass[70]: b[0,2] + 100.0001 delta[0,2,4.0] <= 104.0001
 criterion_fail[70]: b[0,2] + 100.0001 delta[0,2,4.0] >= 4.0001
 contribution_weight[70]: - w[2] + contribution[0,2,4.0] <= 0
 contribution_indicator[70]: - delta[0,2,4.0] + contribution[0,2,4.0] <= 0
 contribution_lower[70]: - w[2] - delta[0,2,4.0] + contribution[0,2,4.0]
   >= -1
 criterion_pass[71]: b[0,2] + 100.0001 delta[0,2,7.0] <= 107.0001
 criterion_fail[71]: b[0,2] + 100.0001 delta[0,2,7.0] >= 7.0001
 contribution_weight[71]: - w[2] + contribution[0,2,7.0] <= 0
 contribution_indicator[71]: - delta[0,2,7.0] + contribution[0,2,7.0] <= 0
 contribution_lower[71]: - w[2] - delta[0,2,7.0] + contribution[0,2,7.0]
   >= -1
 criterion_pass[72]: b[0,2] + 100.0001 delta[0,2,9.0] <= 109.0001
 criterion_fail[72]: b[0,2] + 100.0001 delta[0,2,9.0] >= 9.0001
 contribution_weight[72]: - w[2] + contribution[0,2,9.0] <= 0
 contribution_indicator[72]: - delta[0,2,9.0] + contribution[0,2,9.0] <= 0
 contribution_lower[72]: - w[2] - delta[0,2,9.0] + contribution[0,2,9.0]
   >= -1
 criterion_pass[73]: b[0,2] + 100.0001 delta[0,2,12.0] <= 112.0001
 criterion_fail[73]: b[0,2] + 100.0001 delta[0,2,12.0] >= 12.0001
 contribution_weight[73]: - w[2] + contribution[0,2,12.0] <= 0
 contribution_indicator[73]: - delta[0,2,12.0] + contribution[0,2,12.0]
   <= 0
 contribution_lower[73]: - w[2] - delta[0,2,12.0] + contribution[0,2,12.0]
   >= -1
 criterion_pass[74]: b[0,2] + 100.0001 delta[0,2,13.0] <= 113.0001
 criterion_fail[74]: b[0,2] + 100.0001 delta[0,2,13.0] >= 13.0001
 contribution_weight[74]: - w[2] + contribution[0,2,13.0] <= 0
 contribution_indicator[74]: - delta[0,2,13.0] + contribution[0,2,13.0]
   <= 0
 contribution_lower[74]: - w[2] - delta[0,2,13.0] + contribution[0,2,13.0]
   >= -1
 criterion_pass[75]: b[0,2] + 100.0001 delta[0,2,21.0] <= 121.0001
 criterion_fail[75]: b[0,2] + 100.0001 delta[0,2,21.0] >= 21.0001
 contribution_weight[75]: - w[2] + contribution[0,2,21.0] <= 0
 contribution_indicator[75]: - delta[0,2,21.0] + contribution[0,2,21.0]
   <= 0
 contribution_lower[75]: - w[2] - delta[0,2,21.0] + contribution[0,2,21.0]
   >= -1
 criterion_pass[76]: b[0,2] + 100.0001 delta[0,2,23.0] <= 123.0001
 criterion_fail[76]: b[0,2] + 100.0001 delta[0,2,23.0] >= 23.0001
 contribution_weight[76]: - w[2] + contribution[0,2,23.0] <= 0
 contribution_indicator[76]: - delta[0,2,23.0] + contribution[0,2,23.0]
   <= 0
 contribution_lower[76]: - w[2] - delta[0,2,23.0] + contribution[0,2,23.0]
   >= -1
 criterion_pass[77]: b[0,2] + 100.0001 delta[0,2,27.0] <= 127.0001
 criterion_fail[77]: b[0,2] + 100.0001 delta[0,2,27.0] >= 27.0001
 contribution_weight[77]: - w[2] + contribution[0,2,27.0] <= 0
 contribution_indicator[77]: - delta[0,2,27.0] + contribution[0,2,27.0]
   <= 0
 contribution_lower[77]: - w[2] - delta[0,2,27.0] + contribution[0,2,27.0]
   >= -1
 criterion_pass[78]: b[0,2] + 100.0001 delta[0,2,29.0] <= 129.0001
 criterion_fail[78]: b[0,2] + 100.0001 delta[0,2,29.0] >= 29.0001
 contribution_weight[78]: - w[2] + contribution[0,2,29.0] <= 0
 contribution_indicator[78]: - delta[0,2,29.0] + contribution[0,2,29.0]
   <= 0
 contribution_lower[78]: - w[2] - delta[0,2,29.0] + contribution[0,2,29.0]
   >= -1
 criterion_pass[79]: b[0,2] + 100.0001 delta[0,2,37.0] <= 137.0001
 criterion_fail[79]: b[0,2] + 100.0001 delta[0,2,37.0] >= 37.0001
 contribution_weight[79]: - w[2] + contribution[0,2,37.0] <= 0
 contribution_indicator[79]: - delta[0,2,37.0] + contribution[0,2,37.0]
   <= 0
 contribution_lower[79]: - w[2] - delta[0,2,37.0] + contribution[0,2,37.0]
   >= -1
 criterion_pass[80]: b[0,2] + 100.0001 delta[0,2,38.0] <= 138.0001
 criterion_fail[80]: b[0,2] + 100.0001 delta[0,2,38.0] >= 38.0001
 contribution_weight[80]: - w[2] + contribution[0,2,38.0] <= 0
 contribution_indicator[80]: - delta[0,2,38.0] + contribution[0,2,38.0]
   <= 0
 contribution_lower[80]: - w[2] - delta[0,2,38.0] + contribution[0,2,38.0]
   >= -1
 criterion_pass[81]: b[0,2] + 100.0001 delta[0,2,40.0] <= 140.0001
 criterion_fail[81]: b[0,2] + 100.0001 delta[0,2,40.0] >= 40.0001
 contribution_weight[81]: - w[2] + contribution[0,2,40.0] <= 0
 contribution_indicator[81]: - delta[0,2,40.0] + contribution[0,2,40.0]
   <= 0
 contribution_lower[81]: - w[2] - delta[0,2,40.0] + contribution[0,2,40.0]
   >= -1
 criterion_pass[82]: b[0,2] + 100.0001 delta[0,2,43.0] <= 143.0001
 criterion_fail[82]: b[0,2] + 100.0001 delta[0,2,43.0] >= 43.0001
 contribution_weight[82]: - w[2] + contribution[0,2,43.0] <= 0
 contribution_indicator[82]: - delta[0,2,43.0] + contribution[0,2,43.0]
   <= 0
 contribution_lower[82]: - w[2] - delta[0,2,43.0] + contribution[0,2,43.0]
   >= -1
 criterion_pass[83]: b[0,2] + 100.0001 delta[0,2,55.0] <= 155.0001
 criterion_fail[83]: b[0,2] + 100.0001 delta[0,2,55.0] >= 55.0001
 contribution_weight[83]: - w[2] + contribution[0,2,55.0] <= 0
 contribution_indicator[83]: - delta[0,2,55.0] + contribution[0,2,55.0]
   <= 0
 contribution_lower[83]: - w[2] - delta[0,2,55.0] + contribution[0,2,55.0]
   >= -1
 criterion_pass[84]: b[0,2] + 100.0001 delta[0,2,60.0] <= 160.0001
 criterion_fail[84]: b[0,2] + 100.0001 delta[0,2,60.0] >= 60.0001
 contribution_weight[84]: - w[2] + contribution[0,2,60.0] <= 0
 contribution_indicator[84]: - delta[0,2,60.0] + contribution[0,2,60.0]
   <= 0
 contribution_lower[84]: - w[2] - delta[0,2,60.0] + contribution[0,2,60.0]
   >= -1
 criterion_pass[85]: b[0,2] + 100.0001 delta[0,2,66.0] <= 166.0001
 criterion_fail[85]: b[0,2] + 100.0001 delta[0,2,66.0] >= 66.0001
 contribution_weight[85]: - w[2] + contribution[0,2,66.0] <= 0
 contribution_indicator[85]: - delta[0,2,66.0] + contribution[0,2,66.0]
   <= 0
 contribution_lower[85]: - w[2] - delta[0,2,66.0] + contribution[0,2,66.0]
   >= -1
 criterion_pass[86]: b[0,2] + 100.0001 delta[0,2,69.0] <= 169.0001
 criterion_fail[86]: b[0,2] + 100.0001 delta[0,2,69.0] >= 69.0001
 contribution_weight[86]: - w[2] + contribution[0,2,69.0] <= 0
 contribution_indicator[86]: - delta[0,2,69.0] + contribution[0,2,69.0]
   <= 0
 contribution_lower[86]: - w[2] - delta[0,2,69.0] + contribution[0,2,69.0]
   >= -1
 criterion_pass[87]: b[0,2] + 100.0001 delta[0,2,72.0] <= 172.0001
 criterion_fail[87]: b[0,2] + 100.0001 delta[0,2,72.0] >= 72.0001
 contribution_weight[87]: - w[2] + contribution[0,2,72.0] <= 0
 contribution_indicator[87]: - delta[0,2,72.0] + contribution[0,2,72.0]
   <= 0
 contribution_lower[87]: - w[2] - delta[0,2,72.0] + contribution[0,2,72.0]
   >= -1
 criterion_pass[88]: b[0,2] + 100.0001 delta[0,2,73.0] <= 173.0001
 criterion_fail[88]: b[0,2] + 100.0001 delta[0,2,73.0] >= 73.0001
 contribution_weight[88]: - w[2] + contribution[0,2,73.0] <= 0
 contribution_indicator[88]: - delta[0,2,73.0] + contribution[0,2,73.0]
   <= 0
 contribution_lower[88]: - w[2] - delta[0,2,73.0] + contribution[0,2,73.0]
   >= -1
 criterion_pass[89]: b[0,2] + 100.0001 delta[0,2,74.0] <= 174.0001
 criterion_fail[89]: b[0,2] + 100.0001 delta[0,2,74.0] >= 74.0001
 contribution_weight[89]: - w[2] + contribution[0,2,74.0] <= 0
 contribution_indicator[89]: - delta[0,2,74.0] + contribution[0,2,74.0]
   <= 0
 contribution_lower[89]: - w[2] - delta[0,2,74.0] + contribution[0,2,74.0]
   >= -1
 criterion_pass[90]: b[0,2] + 100.0001 delta[0,2,76.0] <= 176.0001
 criterion_fail[90]: b[0,2] + 100.0001 delta[0,2,76.0] >= 76.0001
 contribution_weight[90]: - w[2] + contribution[0,2,76.0] <= 0
 contribution_indicator[90]: - delta[0,2,76.0] + contribution[0,2,76.0]
   <= 0
 contribution_lower[90]: - w[2] - delta[0,2,76.0] + contribution[0,2,76.0]
   >= -1
 criterion_pass[91]: b[0,2] + 100.0001 delta[0,2,77.0] <= 177.0001
 criterion_fail[91]: b[0,2] + 100.0001 delta[0,2,77.0] >= 77.0001
 contribution_weight[91]: - w[2] + contribution[0,2,77.0] <= 0
 contribution_indicator[91]: - delta[0,2,77.0] + contribution[0,2,77.0]
   <= 0
 contribution_lower[91]: - w[2] - delta[0,2,77.0] + contribution[0,2,77.0]
   >= -1
 criterion_pass[92]: b[0,2] + 100.0001 delta[0,2,78.0] <= 178.0001
 criterion_fail[92]: b[0,2] + 100.0001 delta[0,2,78.0] >= 78.0001
 contribution_weight[92]: - w[2] + contribution[0,2,78.0] <= 0
 contribution_indicator[92]: - delta[0,2,78.0] + contribution[0,2,78.0]
   <= 0
 contribution_lower[92]: - w[2] - delta[0,2,78.0] + contribution[0,2,78.0]
   >= -1
 criterion_pass[93]: b[0,2] + 100.0001 delta[0,2,80.0] <= 180.0001
 criterion_fail[93]: b[0,2] + 100.0001 delta[0,2,80.0] >= 80.0001
 contribution_weight[93]: - w[2] + contribution[0,2,80.0] <= 0
 contribution_indicator[93]: - delta[0,2,80.0] + contribution[0,2,80.0]
   <= 0
 contribution_lower[93]: - w[2] - delta[0,2,80.0] + contribution[0,2,80.0]
   >= -1
 criterion_pass[94]: b[0,2] + 100.0001 delta[0,2,84.0] <= 184.0001
 criterion_fail[94]: b[0,2] + 100.0001 delta[0,2,84.0] >= 84.0001
 contribution_weight[94]: - w[2] + contribution[0,2,84.0] <= 0
 contribution_indicator[94]: - delta[0,2,84.0] + contribution[0,2,84.0]
   <= 0
 contribution_lower[94]: - w[2] - delta[0,2,84.0] + contribution[0,2,84.0]
   >= -1
 criterion_pass[95]: b[0,2] + 100.0001 delta[0,2,88.0] <= 188.0001
 criterion_fail[95]: b[0,2] + 100.0001 delta[0,2,88.0] >= 88.0001
 contribution_weight[95]: - w[2] + contribution[0,2,88.0] <= 0
 contribution_indicator[95]: - delta[0,2,88.0] + contribution[0,2,88.0]
   <= 0
 contribution_lower[95]: - w[2] - delta[0,2,88.0] + contribution[0,2,88.0]
   >= -1
 criterion_pass[96]: b[0,2] + 100.0001 delta[0,2,93.0] <= 193.0001
 criterion_fail[96]: b[0,2] + 100.0001 delta[0,2,93.0] >= 93.0001
 contribution_weight[96]: - w[2] + contribution[0,2,93.0] <= 0
 contribution_indicator[96]: - delta[0,2,93.0] + contribution[0,2,93.0]
   <= 0
 contribution_lower[96]: - w[2] - delta[0,2,93.0] + contribution[0,2,93.0]
   >= -1
 criterion_pass[97]: b[0,2] + 100.0001 delta[0,2,97.0] <= 197.0001
 criterion_fail[97]: b[0,2] + 100.0001 delta[0,2,97.0] >= 97.0001
 contribution_weight[97]: - w[2] + contribution[0,2,97.0] <= 0
 contribution_indicator[97]: - delta[0,2,97.0] + contribution[0,2,97.0]
   <= 0
 contribution_lower[97]: - w[2] - delta[0,2,97.0] + contribution[0,2,97.0]
   >= -1
 criterion_pass[98]: b[0,2] + 100.0001 delta[0,2,99.0] <= 199.0001
 criterion_fail[98]: b[0,2] + 100.0001 delta[0,2,99.0] >= 99.0001
 contribution_weight[98]: - w[2] + contribution[0,2,99.0] <= 0
 contribution_indicator[98]: - delta[0,2,99.0] + contribution[0,2,99.0]
   <= 0
 contribution_lower[98]: - w[2] - delta[0,2,99.0] + contribution[0,2,99.0]
   >= -1
 criterion_pass[99]: b[0,2] + 100.0001 delta[0,2,100.0] <= 200.0001
 criterion_fail[99]: b[0,2] + 100.0001 delta[0,2,100.0] >= 100.0001
 contribution_weight[99]: - w[2] + contribution[0,2,100.0] <= 0
 contribution_indicator[99]: - delta[0,2,100.0] + contribution[0,2,100.0]
   <= 0
 contribution_lower[99]: - w[2] - delta[0,2,100.0]
   + contribution[0,2,100.0] >= -1
 criterion_pass[100]: b[0,3] + 100.0001 delta[0,3,0.0] <= 100.0001
 criterion_fail[100]: b[0,3] + 100.0001 delta[0,3,0.0] >= 0.0001
 contribution_weight[100]: - w[3] + contribution[0,3,0.0] <= 0
 contribution_indicator[100]: - delta[0,3,0.0] + contribution[0,3,0.0]
   <= 0
 contribution_lower[100]: - w[3] - delta[0,3,0.0] + contribution[0,3,0.0]
   >= -1
 criterion_pass[101]: b[0,3] + 100.0001 delta[0,3,2.0] <= 102.0001
 criterion_fail[101]: b[0,3] + 100.0001 delta[0,3,2.0] >= 2.0001
 contribution_weight[101]: - w[3] + contribution[0,3,2.0] <= 0
 contribution_indicator[101]: - delta[0,3,2.0] + contribution[0,3,2.0]
   <= 0
 contribution_lower[101]: - w[3] - delta[0,3,2.0] + contribution[0,3,2.0]
   >= -1
 criterion_pass[102]: b[0,3] + 100.0001 delta[0,3,13.0] <= 113.0001
 criterion_fail[102]: b[0,3] + 100.0001 delta[0,3,13.0] >= 13.0001
 contribution_weight[102]: - w[3] + contribution[0,3,13.0] <= 0
 contribution_indicator[102]: - delta[0,3,13.0] + contribution[0,3,13.0]
   <= 0
 contribution_lower[102]: - w[3] - delta[0,3,13.0] + contribution[0,3,13.0]
   >= -1
 criterion_pass[103]: b[0,3] + 100.0001 delta[0,3,18.0] <= 118.0001
 criterion_fail[103]: b[0,3] + 100.0001 delta[0,3,18.0] >= 18.0001
 contribution_weight[103]: - w[3] + contribution[0,3,18.0] <= 0
 contribution_indicator[103]: - delta[0,3,18.0] + contribution[0,3,18.0]
   <= 0
 contribution_lower[103]: - w[3] - delta[0,3,18.0] + contribution[0,3,18.0]
   >= -1
 criterion_pass[104]: b[0,3] + 100.0001 delta[0,3,19.0] <= 119.0001
 criterion_fail[104]: b[0,3] + 100.0001 delta[0,3,19.0] >= 19.0001
 contribution_weight[104]: - w[3] + contribution[0,3,19.0] <= 0
 contribution_indicator[104]: - delta[0,3,19.0] + contribution[0,3,19.0]
   <= 0
 contribution_lower[104]: - w[3] - delta[0,3,19.0] + contribution[0,3,19.0]
   >= -1
 criterion_pass[105]: b[0,3] + 100.0001 delta[0,3,23.0] <= 123.0001
 criterion_fail[105]: b[0,3] + 100.0001 delta[0,3,23.0] >= 23.0001
 contribution_weight[105]: - w[3] + contribution[0,3,23.0] <= 0
 contribution_indicator[105]: - delta[0,3,23.0] + contribution[0,3,23.0]
   <= 0
 contribution_lower[105]: - w[3] - delta[0,3,23.0] + contribution[0,3,23.0]
   >= -1
 criterion_pass[106]: b[0,3] + 100.0001 delta[0,3,26.0] <= 126.0001
 criterion_fail[106]: b[0,3] + 100.0001 delta[0,3,26.0] >= 26.0001
 contribution_weight[106]: - w[3] + contribution[0,3,26.0] <= 0
 contribution_indicator[106]: - delta[0,3,26.0] + contribution[0,3,26.0]
   <= 0
 contribution_lower[106]: - w[3] - delta[0,3,26.0] + contribution[0,3,26.0]
   >= -1
 criterion_pass[107]: b[0,3] + 100.0001 delta[0,3,31.0] <= 131.0001
 criterion_fail[107]: b[0,3] + 100.0001 delta[0,3,31.0] >= 31.0001
 contribution_weight[107]: - w[3] + contribution[0,3,31.0] <= 0
 contribution_indicator[107]: - delta[0,3,31.0] + contribution[0,3,31.0]
   <= 0
 contribution_lower[107]: - w[3] - delta[0,3,31.0] + contribution[0,3,31.0]
   >= -1
 criterion_pass[108]: b[0,3] + 100.0001 delta[0,3,33.0] <= 133.0001
 criterion_fail[108]: b[0,3] + 100.0001 delta[0,3,33.0] >= 33.0001
 contribution_weight[108]: - w[3] + contribution[0,3,33.0] <= 0
 contribution_indicator[108]: - delta[0,3,33.0] + contribution[0,3,33.0]
   <= 0
 contribution_lower[108]: - w[3] - delta[0,3,33.0] + contribution[0,3,33.0]
   >= -1
 criterion_pass[109]: b[0,3] + 100.0001 delta[0,3,35.0] <= 135.0001
 criterion_fail[109]: b[0,3] + 100.0001 delta[0,3,35.0] >= 35.0001
 contribution_weight[109]: - w[3] + contribution[0,3,35.0] <= 0
 contribution_indicator[109]: - delta[0,3,35.0] + contribution[0,3,35.0]
   <= 0
 contribution_lower[109]: - w[3] - delta[0,3,35.0] + contribution[0,3,35.0]
   >= -1
 criterion_pass[110]: b[0,3] + 100.0001 delta[0,3,36.0] <= 136.0001
 criterion_fail[110]: b[0,3] + 100.0001 delta[0,3,36.0] >= 36.0001
 contribution_weight[110]: - w[3] + contribution[0,3,36.0] <= 0
 contribution_indicator[110]: - delta[0,3,36.0] + contribution[0,3,36.0]
   <= 0
 contribution_lower[110]: - w[3] - delta[0,3,36.0] + contribution[0,3,36.0]
   >= -1
 criterion_pass[111]: b[0,3] + 100.0001 delta[0,3,37.0] <= 137.0001
 criterion_fail[111]: b[0,3] + 100.0001 delta[0,3,37.0] >= 37.0001
 contribution_weight[111]: - w[3] + contribution[0,3,37.0] <= 0
 contribution_indicator[111]: - delta[0,3,37.0] + contribution[0,3,37.0]
   <= 0
 contribution_lower[111]: - w[3] - delta[0,3,37.0] + contribution[0,3,37.0]
   >= -1
 criterion_pass[112]: b[0,3] + 100.0001 delta[0,3,38.0] <= 138.0001
 criterion_fail[112]: b[0,3] + 100.0001 delta[0,3,38.0] >= 38.0001
 contribution_weight[112]: - w[3] + contribution[0,3,38.0] <= 0
 contribution_indicator[112]: - delta[0,3,38.0] + contribution[0,3,38.0]
   <= 0
 contribution_lower[112]: - w[3] - delta[0,3,38.0] + contribution[0,3,38.0]
   >= -1
 criterion_pass[113]: b[0,3] + 100.0001 delta[0,3,39.0] <= 139.0001
 criterion_fail[113]: b[0,3] + 100.0001 delta[0,3,39.0] >= 39.0001
 contribution_weight[113]: - w[3] + contribution[0,3,39.0] <= 0
 contribution_indicator[113]: - delta[0,3,39.0] + contribution[0,3,39.0]
   <= 0
 contribution_lower[113]: - w[3] - delta[0,3,39.0] + contribution[0,3,39.0]
   >= -1
 criterion_pass[114]: b[0,3] + 100.0001 delta[0,3,41.0] <= 141.0001
 criterion_fail[114]: b[0,3] + 100.0001 delta[0,3,41.0] >= 41.0001
 contribution_weight[114]: - w[3] + contribution[0,3,41.0] <= 0
 contribution_indicator[114]: - delta[0,3,41.0] + contribution[0,3,41.0]
   <= 0
 contribution_lower[114]: - w[3] - delta[0,3,41.0] + contribution[0,3,41.0]
   >= -1
 criterion_pass[115]: b[0,3] + 100.0001 delta[0,3,43.0] <= 143.0001
 criterion_fail[115]: b[0,3] + 100.0001 delta[0,3,43.0] >= 43.0001
 contribution_weight[115]: - w[3] + contribution[0,3,43.0] <= 0
 contribution_indicator[115]: - delta[0,3,43.0] + contribution[0,3,43.0]
   <= 0
 contribution_lower[115]: - w[3] - delta[0,3,43.0] + contribution[0,3,43.0]
   >= -1
 criterion_pass[116]: b[0,3] + 100.0001 delta[0,3,44.0] <= 144.0001
 criterion_fail[116]: b[0,3] + 100.0001 delta[0,3,44.0] >= 44.0001
 contribution_weight[116]: - w[3] + contribution[0,3,44.0] <= 0
 contribution_indicator[116]: - delta[0,3,44.0] + contribution[0,3,44.0]
   <= 0
 contribution_lower[116]: - w[3] - delta[0,3,44.0] + contribution[0,3,44.0]
   >= -1
 criterion_pass[117]: b[0,3] + 100.0001 delta[0,3,47.0] <= 147.0001
 criterion_fail[117]: b[0,3] + 100.0001 delta[0,3,47.0] >= 47.0001
 contribution_weight[117]: - w[3] + contribution[0,3,47.0] <= 0
 contribution_indicator[117]: - delta[0,3,47.0] + contribution[0,3,47.0]
   <= 0
 contribution_lower[117]: - w[3] - delta[0,3,47.0] + contribution[0,3,47.0]
   >= -1
 criterion_pass[118]: b[0,3] + 100.0001 delta[0,3,48.0] <= 148.0001
 criterion_fail[118]: b[0,3] + 100.0001 delta[0,3,48.0] >= 48.0001
 contribution_weight[118]: - w[3] + contribution[0,3,48.0] <= 0
 contribution_indicator[118]: - delta[0,3,48.0] + contribution[0,3,48.0]
   <= 0
 contribution_lower[118]: - w[3] - delta[0,3,48.0] + contribution[0,3,48.0]
   >= -1
 criterion_pass[119]: b[0,3] + 100.0001 delta[0,3,51.0] <= 151.0001
 criterion_fail[119]: b[0,3] + 100.0001 delta[0,3,51.0] >= 51.0001
 contribution_weight[119]: - w[3] + contribution[0,3,51.0] <= 0
 contribution_indicator[119]: - delta[0,3,51.0] + contribution[0,3,51.0]
   <= 0
 contribution_lower[119]: - w[3] - delta[0,3,51.0] + contribution[0,3,51.0]
   >= -1
 criterion_pass[120]: b[0,3] + 100.0001 delta[0,3,53.0] <= 153.0001
 criterion_fail[120]: b[0,3] + 100.0001 delta[0,3,53.0] >= 53.0001
 contribution_weight[120]: - w[3] + contribution[0,3,53.0] <= 0
 contribution_indicator[120]: - delta[0,3,53.0] + contribution[0,3,53.0]
   <= 0
 contribution_lower[120]: - w[3] - delta[0,3,53.0] + contribution[0,3,53.0]
   >= -1
 criterion_pass[121]: b[0,3] + 100.0001 delta[0,3,54.0] <= 154.0001
 criterion_fail[121]: b[0,3] + 100.0001 delta[0,3,54.0] >= 54.0001
 contribution_weight[121]: - w[3] + contribution[0,3,54.0] <= 0
 contribution_indicator[121]: - delta[0,3,54.0] + contribution[0,3,54.0]
   <= 0
 contribution_lower[121]: - w[3] - delta[0,3,54.0] + contribution[0,3,54.0]
   >= -1
 criterion_pass[122]: b[0,3] + 100.0001 delta[0,3,56.0] <= 156.0001
 criterion_fail[122]: b[0,3] + 100.0001 delta[0,3,56.0] >= 56.0001
 contribution_weight[122]: - w[3] + contribution[0,3,56.0] <= 0
 contribution_indicator[122]: - delta[0,3,56.0] + contribution[0,3,56.0]
   <= 0
 contribution_lower[122]: - w[3] - delta[0,3,56.0] + contribution[0,3,56.0]
   >= -1
 criterion_pass[123]: b[0,3] + 100.0001 delta[0,3,57.0] <= 157.0001
 criterion_fail[123]: b[0,3] + 100.0001 delta[0,3,57.0] >= 57.0001
 contribution_weight[123]: - w[3] + contribution[0,3,57.0] <= 0
 contribution_indicator[123]: - delta[0,3,57.0] + contribution[0,3,57.0]
   <= 0
 contribution_lower[123]: - w[3] - delta[0,3,57.0] + contribution[0,3,57.0]
   >= -1
 criterion_pass[124]: b[0,3] + 100.0001 delta[0,3,62.0] <= 162.0001
 criterion_fail[124]: b[0,3] + 100.0001 delta[0,3,62.0] >= 62.0001
 contribution_weight[124]: - w[3] + contribution[0,3,62.0] <= 0
 contribution_indicator[124]: - delta[0,3,62.0] + contribution[0,3,62.0]
   <= 0
 contribution_lower[124]: - w[3] - delta[0,3,62.0] + contribution[0,3,62.0]
   >= -1
 criterion_pass[125]: b[0,3] + 100.0001 delta[0,3,65.0] <= 165.0001
 criterion_fail[125]: b[0,3] + 100.0001 delta[0,3,65.0] >= 65.0001
 contribution_weight[125]: - w[3] + contribution[0,3,65.0] <= 0
 contribution_indicator[125]: - delta[0,3,65.0] + contribution[0,3,65.0]
   <= 0
 contribution_lower[125]: - w[3] - delta[0,3,65.0] + contribution[0,3,65.0]
   >= -1
 criterion_pass[126]: b[0,3] + 100.0001 delta[0,3,75.0] <= 175.0001
 criterion_fail[126]: b[0,3] + 100.0001 delta[0,3,75.0] >= 75.0001
 contribution_weight[126]: - w[3] + contribution[0,3,75.0] <= 0
 contribution_indicator[126]: - delta[0,3,75.0] + contribution[0,3,75.0]
   <= 0
 contribution_lower[126]: - w[3] - delta[0,3,75.0] + contribution[0,3,75.0]
   >= -1
 criterion_pass[127]: b[0,3] + 100.0001 delta[0,3,76.0] <= 176.0001
 criterion_fail[127]: b[0,3] + 100.0001 delta[0,3,76.0] >= 76.0001
 contribution_weight[127]: - w[3] + contribution[0,3,76.0] <= 0
 contribution_indicator[127]: - delta[0,3,76.0] + contribution[0,3,76.0]
   <= 0
 contribution_lower[127]: - w[3] - delta[0,3,76.0] + contribution[0,3,76.0]
   >= -1
 criterion_pass[128]: b[0,3] + 100.0001 delta[0,3,85.0] <= 185.0001
 criterion_fail[128]: b[0,3] + 100.0001 delta[0,3,85.0] >= 85.0001
 contribution_weight[128]: - w[3] + contribution[0,3,85.0] <= 0
 contribution_indicator[128]: - delta[0,3,85.0] + contribution[0,3,85.0]
   <= 0
 contribution_lower[128]: - w[3] - delta[0,3,85.0] + contribution[0,3,85.0]
   >= -1
 criterion_pass[129]: b[0,3] + 100.0001 delta[0,3,86.0] <= 186.0001
 criterion_fail[129]: b[0,3] + 100.0001 delta[0,3,86.0] >= 86.0001
 contribution_weight[129]: - w[3] + contribution[0,3,86.0] <= 0
 contribution_indicator[129]: - delta[0,3,86.0] + contribution[0,3,86.0]
   <= 0
 contribution_lower[129]: - w[3] - delta[0,3,86.0] + contribution[0,3,86.0]
   >= -1
 criterion_pass[130]: b[0,3] + 100.0001 delta[0,3,88.0] <= 188.0001
 criterion_fail[130]: b[0,3] + 100.0001 delta[0,3,88.0] >= 88.0001
 contribution_weight[130]: - w[3] + contribution[0,3,88.0] <= 0
 contribution_indicator[130]: - delta[0,3,88.0] + contribution[0,3,88.0]
   <= 0
 contribution_lower[130]: - w[3] - delta[0,3,88.0] + contribution[0,3,88.0]
   >= -1
 criterion_pass[131]: b[0,3] + 100.0001 delta[0,3,94.0] <= 194.0001
 criterion_fail[131]: b[0,3] + 100.0001 delta[0,3,94.0] >= 94.0001
 contribution_weight[131]: - w[3] + contribution[0,3,94.0] <= 0
 contribution_indicator[131]: - delta[0,3,94.0] + contribution[0,3,94.0]
   <= 0
 contribution_lower[131]: - w[3] - delta[0,3,94.0] + contribution[0,3,94.0]
   >= -1
 criterion_pass[132]: b[0,4] + 100.0001 delta[0,4,0.0] <= 100.0001
 criterion_fail[132]: b[0,4] + 100.0001 delta[0,4,0.0] >= 0.0001
 contribution_weight[132]: - w[4] + contribution[0,4,0.0] <= 0
 contribution_indicator[132]: - delta[0,4,0.0] + contribution[0,4,0.0]
   <= 0
 contribution_lower[132]: - w[4] - delta[0,4,0.0] + contribution[0,4,0.0]
   >= -1
 criterion_pass[133]: b[0,4] + 100.0001 delta[0,4,2.0] <= 102.0001
 criterion_fail[133]: b[0,4] + 100.0001 delta[0,4,2.0] >= 2.0001
 contribution_weight[133]: - w[4] + contribution[0,4,2.0] <= 0
 contribution_indicator[133]: - delta[0,4,2.0] + contribution[0,4,2.0]
   <= 0
 contribution_lower[133]: - w[4] - delta[0,4,2.0] + contribution[0,4,2.0]
   >= -1
 criterion_pass[134]: b[0,4] + 100.0001 delta[0,4,6.0] <= 106.0001
 criterion_fail[134]: b[0,4] + 100.0001 delta[0,4,6.0] >= 6.0001
 contribution_weight[134]: - w[4] + contribution[0,4,6.0] <= 0
 contribution_indicator[134]: - delta[0,4,6.0] + contribution[0,4,6.0]
   <= 0
 contribution_lower[134]: - w[4] - delta[0,4,6.0] + contribution[0,4,6.0]
   >= -1
 criterion_pass[135]: b[0,4] + 100.0001 delta[0,4,9.0] <= 109.0001
 criterion_fail[135]: b[0,4] + 100.0001 delta[0,4,9.0] >= 9.0001
 contribution_weight[135]: - w[4] + contribution[0,4,9.0] <= 0
 contribution_indicator[135]: - delta[0,4,9.0] + contribution[0,4,9.0]
   <= 0
 contribution_lower[135]: - w[4] - delta[0,4,9.0] + contribution[0,4,9.0]
   >= -1
 criterion_pass[136]: b[0,4] + 100.0001 delta[0,4,13.0] <= 113.0001
 criterion_fail[136]: b[0,4] + 100.0001 delta[0,4,13.0] >= 13.0001
 contribution_weight[136]: - w[4] + contribution[0,4,13.0] <= 0
 contribution_indicator[136]: - delta[0,4,13.0] + contribution[0,4,13.0]
   <= 0
 contribution_lower[136]: - w[4] - delta[0,4,13.0] + contribution[0,4,13.0]
   >= -1
 criterion_pass[137]: b[0,4] + 100.0001 delta[0,4,16.0] <= 116.0001
 criterion_fail[137]: b[0,4] + 100.0001 delta[0,4,16.0] >= 16.0001
 contribution_weight[137]: - w[4] + contribution[0,4,16.0] <= 0
 contribution_indicator[137]: - delta[0,4,16.0] + contribution[0,4,16.0]
   <= 0
 contribution_lower[137]: - w[4] - delta[0,4,16.0] + contribution[0,4,16.0]
   >= -1
 criterion_pass[138]: b[0,4] + 100.0001 delta[0,4,17.0] <= 117.0001
 criterion_fail[138]: b[0,4] + 100.0001 delta[0,4,17.0] >= 17.0001
 contribution_weight[138]: - w[4] + contribution[0,4,17.0] <= 0
 contribution_indicator[138]: - delta[0,4,17.0] + contribution[0,4,17.0]
   <= 0
 contribution_lower[138]: - w[4] - delta[0,4,17.0] + contribution[0,4,17.0]
   >= -1
 criterion_pass[139]: b[0,4] + 100.0001 delta[0,4,19.0] <= 119.0001
 criterion_fail[139]: b[0,4] + 100.0001 delta[0,4,19.0] >= 19.0001
 contribution_weight[139]: - w[4] + contribution[0,4,19.0] <= 0
 contribution_indicator[139]: - delta[0,4,19.0] + contribution[0,4,19.0]
   <= 0
 contribution_lower[139]: - w[4] - delta[0,4,19.0] + contribution[0,4,19.0]
   >= -1
 criterion_pass[140]: b[0,4] + 100.0001 delta[0,4,22.0] <= 122.0001
 criterion_fail[140]: b[0,4] + 100.0001 delta[0,4,22.0] >= 22.0001
 contribution_weight[140]: - w[4] + contribution[0,4,22.0] <= 0
 contribution_indicator[140]: - delta[0,4,22.0] + contribution[0,4,22.0]
   <= 0
 contribution_lower[140]: - w[4] - delta[0,4,22.0] + contribution[0,4,22.0]
   >= -1
 criterion_pass[141]: b[0,4] + 100.0001 delta[0,4,24.0] <= 124.0001
 criterion_fail[141]: b[0,4] + 100.0001 delta[0,4,24.0] >= 24.0001
 contribution_weight[141]: - w[4] + contribution[0,4,24.0] <= 0
 contribution_indicator[141]: - delta[0,4,24.0] + contribution[0,4,24.0]
   <= 0
 contribution_lower[141]: - w[4] - delta[0,4,24.0] + contribution[0,4,24.0]
   >= -1
 criterion_pass[142]: b[0,4] + 100.0001 delta[0,4,30.0] <= 130.0001
 criterion_fail[142]: b[0,4] + 100.0001 delta[0,4,30.0] >= 30.0001
 contribution_weight[142]: - w[4] + contribution[0,4,30.0] <= 0
 contribution_indicator[142]: - delta[0,4,30.0] + contribution[0,4,30.0]
   <= 0
 contribution_lower[142]: - w[4] - delta[0,4,30.0] + contribution[0,4,30.0]
   >= -1
 criterion_pass[143]: b[0,4] + 100.0001 delta[0,4,36.0] <= 136.0001
 criterion_fail[143]: b[0,4] + 100.0001 delta[0,4,36.0] >= 36.0001
 contribution_weight[143]: - w[4] + contribution[0,4,36.0] <= 0
 contribution_indicator[143]: - delta[0,4,36.0] + contribution[0,4,36.0]
   <= 0
 contribution_lower[143]: - w[4] - delta[0,4,36.0] + contribution[0,4,36.0]
   >= -1
 criterion_pass[144]: b[0,4] + 100.0001 delta[0,4,38.0] <= 138.0001
 criterion_fail[144]: b[0,4] + 100.0001 delta[0,4,38.0] >= 38.0001
 contribution_weight[144]: - w[4] + contribution[0,4,38.0] <= 0
 contribution_indicator[144]: - delta[0,4,38.0] + contribution[0,4,38.0]
   <= 0
 contribution_lower[144]: - w[4] - delta[0,4,38.0] + contribution[0,4,38.0]
   >= -1
 criterion_pass[145]: b[0,4] + 100.0001 delta[0,4,40.0] <= 140.0001
 criterion_fail[145]: b[0,4] + 100.0001 delta[0,4,40.0] >= 40.0001
 contribution_weight[145]: - w[4] + contribution[0,4,40.0] <= 0
 contribution_indicator[145]: - delta[0,4,40.0] + contribution[0,4,40.0]
   <= 0
 contribution_lower[145]: - w[4] - delta[0,4,40.0] + contribution[0,4,40.0]
   >= -1
 criterion_pass[146]: b[0,4] + 100.0001 delta[0,4,41.0] <= 141.0001
 criterion_fail[146]: b[0,4] + 100.0001 delta[0,4,41.0] >= 41.0001
 contribution_weight[146]: - w[4] + contribution[0,4,41.0] <= 0
 contribution_indicator[146]: - delta[0,4,41.0] + contribution[0,4,41.0]
   <= 0
 contribution_lower[146]: - w[4] - delta[0,4,41.0] + contribution[0,4,41.0]
   >= -1
 criterion_pass[147]: b[0,4] + 100.0001 delta[0,4,42.0] <= 142.0001
 criterion_fail[147]: b[0,4] + 100.0001 delta[0,4,42.0] >= 42.0001
 contribution_weight[147]: - w[4] + contribution[0,4,42.0] <= 0
 contribution_indicator[147]: - delta[0,4,42.0] + contribution[0,4,42.0]
   <= 0
 contribution_lower[147]: - w[4] - delta[0,4,42.0] + contribution[0,4,42.0]
   >= -1
 criterion_pass[148]: b[0,4] + 100.0001 delta[0,4,43.0] <= 143.0001
 criterion_fail[148]: b[0,4] + 100.0001 delta[0,4,43.0] >= 43.0001
 contribution_weight[148]: - w[4] + contribution[0,4,43.0] <= 0
 contribution_indicator[148]: - delta[0,4,43.0] + contribution[0,4,43.0]
   <= 0
 contribution_lower[148]: - w[4] - delta[0,4,43.0] + contribution[0,4,43.0]
   >= -1
 criterion_pass[149]: b[0,4] + 100.0001 delta[0,4,45.0] <= 145.0001
 criterion_fail[149]: b[0,4] + 100.0001 delta[0,4,45.0] >= 45.0001
 contribution_weight[149]: - w[4] + contribution[0,4,45.0] <= 0
 contribution_indicator[149]: - delta[0,4,45.0] + contribution[0,4,45.0]
   <= 0
 contribution_lower[149]: - w[4] - delta[0,4,45.0] + contribution[0,4,45.0]
   >= -1
 criterion_pass[150]: b[0,4] + 100.0001 delta[0,4,47.0] <= 147.0001
 criterion_fail[150]: b[0,4] + 100.0001 delta[0,4,47.0] >= 47.0001
 contribution_weight[150]: - w[4] + contribution[0,4,47.0] <= 0
 contribution_indicator[150]: - delta[0,4,47.0] + contribution[0,4,47.0]
   <= 0
 contribution_lower[150]: - w[4] - delta[0,4,47.0] + contribution[0,4,47.0]
   >= -1
 criterion_pass[151]: b[0,4] + 100.0001 delta[0,4,48.0] <= 148.0001
 criterion_fail[151]: b[0,4] + 100.0001 delta[0,4,48.0] >= 48.0001
 contribution_weight[151]: - w[4] + contribution[0,4,48.0] <= 0
 contribution_indicator[151]: - delta[0,4,48.0] + contribution[0,4,48.0]
   <= 0
 contribution_lower[151]: - w[4] - delta[0,4,48.0] + contribution[0,4,48.0]
   >= -1
 criterion_pass[152]: b[0,4] + 100.0001 delta[0,4,52.0] <= 152.0001
 criterion_fail[152]: b[0,4] + 100.0001 delta[0,4,52.0] >= 52.0001
 contribution_weight[152]: - w[4] + contribution[0,4,52.0] <= 0
 contribution_indicator[152]: - delta[0,4,52.0] + contribution[0,4,52.0]
   <= 0
 contribution_lower[152]: - w[4] - delta[0,4,52.0] + contribution[0,4,52.0]
   >= -1
 criterion_pass[153]: b[0,4] + 100.0001 delta[0,4,54.0] <= 154.0001
 criterion_fail[153]: b[0,4] + 100.0001 delta[0,4,54.0] >= 54.0001
 contribution_weight[153]: - w[4] + contribution[0,4,54.0] <= 0
 contribution_indicator[153]: - delta[0,4,54.0] + contribution[0,4,54.0]
   <= 0
 contribution_lower[153]: - w[4] - delta[0,4,54.0] + contribution[0,4,54.0]
   >= -1
 criterion_pass[154]: b[0,4] + 100.0001 delta[0,4,56.0] <= 156.0001
 criterion_fail[154]: b[0,4] + 100.0001 delta[0,4,56.0] >= 56.0001
 contribution_weight[154]: - w[4] + contribution[0,4,56.0] <= 0
 contribution_indicator[154]: - delta[0,4,56.0] + contribution[0,4,56.0]
   <= 0
 contribution_lower[154]: - w[4] - delta[0,4,56.0] + contribution[0,4,56.0]
   >= -1
 criterion_pass[155]: b[0,4] + 100.0001 delta[0,4,59.0] <= 159.0001
 criterion_fail[155]: b[0,4] + 100.0001 delta[0,4,59.0] >= 59.0001
 contribution_weight[155]: - w[4] + contribution[0,4,59.0] <= 0
 contribution_indicator[155]: - delta[0,4,59.0] + contribution[0,4,59.0]
   <= 0
 contribution_lower[155]: - w[4] - delta[0,4,59.0] + contribution[0,4,59.0]
   >= -1
 criterion_pass[156]: b[0,4] + 100.0001 delta[0,4,62.0] <= 162.0001
 criterion_fail[156]: b[0,4] + 100.0001 delta[0,4,62.0] >= 62.0001
 contribution_weight[156]: - w[4] + contribution[0,4,62.0] <= 0
 contribution_indicator[156]: - delta[0,4,62.0] + contribution[0,4,62.0]
   <= 0
 contribution_lower[156]: - w[4] - delta[0,4,62.0] + contribution[0,4,62.0]
   >= -1
 criterion_pass[157]: b[0,4] + 100.0001 delta[0,4,64.0] <= 164.0001
 criterion_fail[157]: b[0,4] + 100.0001 delta[0,4,64.0] >= 64.0001
 contribution_weight[157]: - w[4] + contribution[0,4,64.0] <= 0
 contribution_indicator[157]: - delta[0,4,64.0] + contribution[0,4,64.0]
   <= 0
 contribution_lower[157]: - w[4] - delta[0,4,64.0] + contribution[0,4,64.0]
   >= -1
 criterion_pass[158]: b[0,4] + 100.0001 delta[0,4,67.0] <= 167.0001
 criterion_fail[158]: b[0,4] + 100.0001 delta[0,4,67.0] >= 67.0001
 contribution_weight[158]: - w[4] + contribution[0,4,67.0] <= 0
 contribution_indicator[158]: - delta[0,4,67.0] + contribution[0,4,67.0]
   <= 0
 contribution_lower[158]: - w[4] - delta[0,4,67.0] + contribution[0,4,67.0]
   >= -1
 criterion_pass[159]: b[0,4] + 100.0001 delta[0,4,68.0] <= 168.0001
 criterion_fail[159]: b[0,4] + 100.0001 delta[0,4,68.0] >= 68.0001
 contribution_weight[159]: - w[4] + contribution[0,4,68.0] <= 0
 contribution_indicator[159]: - delta[0,4,68.0] + contribution[0,4,68.0]
   <= 0
 contribution_lower[159]: - w[4] - delta[0,4,68.0] + contribution[0,4,68.0]
   >= -1
 criterion_pass[160]: b[0,4] + 100.0001 delta[0,4,76.0] <= 176.0001
 criterion_fail[160]: b[0,4] + 100.0001 delta[0,4,76.0] >= 76.0001
 contribution_weight[160]: - w[4] + contribution[0,4,76.0] <= 0
 contribution_indicator[160]: - delta[0,4,76.0] + contribution[0,4,76.0]
   <= 0
 contribution_lower[160]: - w[4] - delta[0,4,76.0] + contribution[0,4,76.0]
   >= -1
 criterion_pass[161]: b[0,4] + 100.0001 delta[0,4,88.0] <= 188.0001
 criterion_fail[161]: b[0,4] + 100.0001 delta[0,4,88.0] >= 88.0001
 contribution_weight[161]: - w[4] + contribution[0,4,88.0] <= 0
 contribution_indicator[161]: - delta[0,4,88.0] + contribution[0,4,88.0]
   <= 0
 contribution_lower[161]: - w[4] - delta[0,4,88.0] + contribution[0,4,88.0]
   >= -1
 criterion_pass[162]: b[0,4] + 100.0001 delta[0,4,94.0] <= 194.0001
 criterion_fail[162]: b[0,4] + 100.0001 delta[0,4,94.0] >= 94.0001
 contribution_weight[162]: - w[4] + contribution[0,4,94.0] <= 0
 contribution_indicator[162]: - delta[0,4,94.0] + contribution[0,4,94.0]
   <= 0
 contribution_lower[162]: - w[4] - delta[0,4,94.0] + contribution[0,4,94.0]
   >= -1
 criterion_pass[163]: b[0,4] + 100.0001 delta[0,4,99.0] <= 199.0001
 criterion_fail[163]: b[0,4] + 100.0001 delta[0,4,99.0] >= 99.0001
 contribution_weight[163]: - w[4] + contribution[0,4,99.0] <= 0
 contribution_indicator[163]: - delta[0,4,99.0] + contribution[0,4,99.0]
   <= 0
 contribution_lower[163]: - w[4] - delta[0,4,99.0] + contribution[0,4,99.0]
   >= -1
 criterion_pass[164]: b[1,0] + 100.0001 delta[1,0,1.0] <= 101.0001
 criterion_fail[164]: b[1,0] + 100.0001 delta[1,0,1.0] >= 1.0001
 contribution_weight[164]: - w[0] + contribution[1,0,1.0] <= 0
 contribution_indicator[164]: - delta[1,0,1.0] + contribution[1,0,1.0]
   <= 0
 contribution_lower[164]: - w[0] - delta[1,0,1.0] + contribution[1,0,1.0]
   >= -1
 criterion_pass[165]: b[1,0] + 100.0001 delta[1,0,3.0] <= 103.0001
 criterion_fail[165]: b[1,0] + 100.0001 delta[1,0,3.0] >= 3.0001
 contribution_weight[165]: - w[0] + contribution[1,0,3.0] <= 0
 contribution_indicator[165]: - delta[1,0,3.0] + contribution[1,0,3.0]
   <= 0
 contribution_lower[165]: - w[0] - delta[1,0,3.0] + contribution[1,0,3.0]
   >= -1
 criterion_pass[166]: b[1,0] + 100.0001 delta[1,0,5.0] <= 105.0001
 criterion_fail[166]: b[1,0] + 100.0001 delta[1,0,5.0] >= 5.0001
 contribution_weight[166]: - w[0] + contribution[1,0,5.0] <= 0
 contribution_indicator[166]: - delta[1,0,5.0] + contribution[1,0,5.0]
   <= 0
 contribution_lower[166]: - w[0] - delta[1,0,5.0] + contribution[1,0,5.0]
   >= -1
 criterion_pass[167]: b[1,0] + 100.0001 delta[1,0,10.0] <= 110.0001
 criterion_fail[167]: b[1,0] + 100.0001 delta[1,0,10.0] >= 10.0001
 contribution_weight[167]: - w[0] + contribution[1,0,10.0] <= 0
 contribution_indicator[167]: - delta[1,0,10.0] + contribution[1,0,10.0]
   <= 0
 contribution_lower[167]: - w[0] - delta[1,0,10.0] + contribution[1,0,10.0]
   >= -1
 criterion_pass[168]: b[1,0] + 100.0001 delta[1,0,11.0] <= 111.0001
 criterion_fail[168]: b[1,0] + 100.0001 delta[1,0,11.0] >= 11.0001
 contribution_weight[168]: - w[0] + contribution[1,0,11.0] <= 0
 contribution_indicator[168]: - delta[1,0,11.0] + contribution[1,0,11.0]
   <= 0
 contribution_lower[168]: - w[0] - delta[1,0,11.0] + contribution[1,0,11.0]
   >= -1
 criterion_pass[169]: b[1,0] + 100.0001 delta[1,0,16.0] <= 116.0001
 criterion_fail[169]: b[1,0] + 100.0001 delta[1,0,16.0] >= 16.0001
 contribution_weight[169]: - w[0] + contribution[1,0,16.0] <= 0
 contribution_indicator[169]: - delta[1,0,16.0] + contribution[1,0,16.0]
   <= 0
 contribution_lower[169]: - w[0] - delta[1,0,16.0] + contribution[1,0,16.0]
   >= -1
 criterion_pass[170]: b[1,0] + 100.0001 delta[1,0,19.0] <= 119.0001
 criterion_fail[170]: b[1,0] + 100.0001 delta[1,0,19.0] >= 19.0001
 contribution_weight[170]: - w[0] + contribution[1,0,19.0] <= 0
 contribution_indicator[170]: - delta[1,0,19.0] + contribution[1,0,19.0]
   <= 0
 contribution_lower[170]: - w[0] - delta[1,0,19.0] + contribution[1,0,19.0]
   >= -1
 criterion_pass[171]: b[1,0] + 100.0001 delta[1,0,22.0] <= 122.0001
 criterion_fail[171]: b[1,0] + 100.0001 delta[1,0,22.0] >= 22.0001
 contribution_weight[171]: - w[0] + contribution[1,0,22.0] <= 0
 contribution_indicator[171]: - delta[1,0,22.0] + contribution[1,0,22.0]
   <= 0
 contribution_lower[171]: - w[0] - delta[1,0,22.0] + contribution[1,0,22.0]
   >= -1
 criterion_pass[172]: b[1,0] + 100.0001 delta[1,0,30.0] <= 130.0001
 criterion_fail[172]: b[1,0] + 100.0001 delta[1,0,30.0] >= 30.0001
 contribution_weight[172]: - w[0] + contribution[1,0,30.0] <= 0
 contribution_indicator[172]: - delta[1,0,30.0] + contribution[1,0,30.0]
   <= 0
 contribution_lower[172]: - w[0] - delta[1,0,30.0] + contribution[1,0,30.0]
   >= -1
 criterion_pass[173]: b[1,0] + 100.0001 delta[1,0,36.0] <= 136.0001
 criterion_fail[173]: b[1,0] + 100.0001 delta[1,0,36.0] >= 36.0001
 contribution_weight[173]: - w[0] + contribution[1,0,36.0] <= 0
 contribution_indicator[173]: - delta[1,0,36.0] + contribution[1,0,36.0]
   <= 0
 contribution_lower[173]: - w[0] - delta[1,0,36.0] + contribution[1,0,36.0]
   >= -1
 criterion_pass[174]: b[1,0] + 100.0001 delta[1,0,37.0] <= 137.0001
 criterion_fail[174]: b[1,0] + 100.0001 delta[1,0,37.0] >= 37.0001
 contribution_weight[174]: - w[0] + contribution[1,0,37.0] <= 0
 contribution_indicator[174]: - delta[1,0,37.0] + contribution[1,0,37.0]
   <= 0
 contribution_lower[174]: - w[0] - delta[1,0,37.0] + contribution[1,0,37.0]
   >= -1
 criterion_pass[175]: b[1,0] + 100.0001 delta[1,0,38.0] <= 138.0001
 criterion_fail[175]: b[1,0] + 100.0001 delta[1,0,38.0] >= 38.0001
 contribution_weight[175]: - w[0] + contribution[1,0,38.0] <= 0
 contribution_indicator[175]: - delta[1,0,38.0] + contribution[1,0,38.0]
   <= 0
 contribution_lower[175]: - w[0] - delta[1,0,38.0] + contribution[1,0,38.0]
   >= -1
 criterion_pass[176]: b[1,0] + 100.0001 delta[1,0,40.0] <= 140.0001
 criterion_fail[176]: b[1,0] + 100.0001 delta[1,0,40.0] >= 40.0001
 contribution_weight[176]: - w[0] + contribution[1,0,40.0] <= 0
 contribution_indicator[176]: - delta[1,0,40.0] + contribution[1,0,40.0]
   <= 0
 contribution_lower[176]: - w[0] - delta[1,0,40.0] + contribution[1,0,40.0]
   >= -1
 criterion_pass[177]: b[1,0] + 100.0001 delta[1,0,41.0] <= 141.0001
 criterion_fail[177]: b[1,0] + 100.0001 delta[1,0,41.0] >= 41.0001
 contribution_weight[177]: - w[0] + contribution[1,0,41.0] <= 0
 contribution_indicator[177]: - delta[1,0,41.0] + contribution[1,0,41.0]
   <= 0
 contribution_lower[177]: - w[0] - delta[1,0,41.0] + contribution[1,0,41.0]
   >= -1
 criterion_pass[178]: b[1,0] + 100.0001 delta[1,0,47.0] <= 147.0001
 criterion_fail[178]: b[1,0] + 100.0001 delta[1,0,47.0] >= 47.0001
 contribution_weight[178]: - w[0] + contribution[1,0,47.0] <= 0
 contribution_indicator[178]: - delta[1,0,47.0] + contribution[1,0,47.0]
   <= 0
 contribution_lower[178]: - w[0] - delta[1,0,47.0] + contribution[1,0,47.0]
   >= -1
 criterion_pass[179]: b[1,0] + 100.0001 delta[1,0,49.0] <= 149.0001
 criterion_fail[179]: b[1,0] + 100.0001 delta[1,0,49.0] >= 49.0001
 contribution_weight[179]: - w[0] + contribution[1,0,49.0] <= 0
 contribution_indicator[179]: - delta[1,0,49.0] + contribution[1,0,49.0]
   <= 0
 contribution_lower[179]: - w[0] - delta[1,0,49.0] + contribution[1,0,49.0]
   >= -1
 criterion_pass[180]: b[1,0] + 100.0001 delta[1,0,54.0] <= 154.0001
 criterion_fail[180]: b[1,0] + 100.0001 delta[1,0,54.0] >= 54.0001
 contribution_weight[180]: - w[0] + contribution[1,0,54.0] <= 0
 contribution_indicator[180]: - delta[1,0,54.0] + contribution[1,0,54.0]
   <= 0
 contribution_lower[180]: - w[0] - delta[1,0,54.0] + contribution[1,0,54.0]
   >= -1
 criterion_pass[181]: b[1,0] + 100.0001 delta[1,0,56.0] <= 156.0001
 criterion_fail[181]: b[1,0] + 100.0001 delta[1,0,56.0] >= 56.0001
 contribution_weight[181]: - w[0] + contribution[1,0,56.0] <= 0
 contribution_indicator[181]: - delta[1,0,56.0] + contribution[1,0,56.0]
   <= 0
 contribution_lower[181]: - w[0] - delta[1,0,56.0] + contribution[1,0,56.0]
   >= -1
 criterion_pass[182]: b[1,0] + 100.0001 delta[1,0,58.0] <= 158.0001
 criterion_fail[182]: b[1,0] + 100.0001 delta[1,0,58.0] >= 58.0001
 contribution_weight[182]: - w[0] + contribution[1,0,58.0] <= 0
 contribution_indicator[182]: - delta[1,0,58.0] + contribution[1,0,58.0]
   <= 0
 contribution_lower[182]: - w[0] - delta[1,0,58.0] + contribution[1,0,58.0]
   >= -1
 criterion_pass[183]: b[1,0] + 100.0001 delta[1,0,59.0] <= 159.0001
 criterion_fail[183]: b[1,0] + 100.0001 delta[1,0,59.0] >= 59.0001
 contribution_weight[183]: - w[0] + contribution[1,0,59.0] <= 0
 contribution_indicator[183]: - delta[1,0,59.0] + contribution[1,0,59.0]
   <= 0
 contribution_lower[183]: - w[0] - delta[1,0,59.0] + contribution[1,0,59.0]
   >= -1
 criterion_pass[184]: b[1,0] + 100.0001 delta[1,0,60.0] <= 160.0001
 criterion_fail[184]: b[1,0] + 100.0001 delta[1,0,60.0] >= 60.0001
 contribution_weight[184]: - w[0] + contribution[1,0,60.0] <= 0
 contribution_indicator[184]: - delta[1,0,60.0] + contribution[1,0,60.0]
   <= 0
 contribution_lower[184]: - w[0] - delta[1,0,60.0] + contribution[1,0,60.0]
   >= -1
 criterion_pass[185]: b[1,0] + 100.0001 delta[1,0,64.0] <= 164.0001
 criterion_fail[185]: b[1,0] + 100.0001 delta[1,0,64.0] >= 64.0001
 contribution_weight[185]: - w[0] + contribution[1,0,64.0] <= 0
 contribution_indicator[185]: - delta[1,0,64.0] + contribution[1,0,64.0]
   <= 0
 contribution_lower[185]: - w[0] - delta[1,0,64.0] + contribution[1,0,64.0]
   >= -1
 criterion_pass[186]: b[1,0] + 100.0001 delta[1,0,66.0] <= 166.0001
 criterion_fail[186]: b[1,0] + 100.0001 delta[1,0,66.0] >= 66.0001
 contribution_weight[186]: - w[0] + contribution[1,0,66.0] <= 0
 contribution_indicator[186]: - delta[1,0,66.0] + contribution[1,0,66.0]
   <= 0
 contribution_lower[186]: - w[0] - delta[1,0,66.0] + contribution[1,0,66.0]
   >= -1
 criterion_pass[187]: b[1,0] + 100.0001 delta[1,0,68.0] <= 168.0001
 criterion_fail[187]: b[1,0] + 100.0001 delta[1,0,68.0] >= 68.0001
 contribution_weight[187]: - w[0] + contribution[1,0,68.0] <= 0
 contribution_indicator[187]: - delta[1,0,68.0] + contribution[1,0,68.0]
   <= 0
 contribution_lower[187]: - w[0] - delta[1,0,68.0] + contribution[1,0,68.0]
   >= -1
 criterion_pass[188]: b[1,0] + 100.0001 delta[1,0,70.0] <= 170.0001
 criterion_fail[188]: b[1,0] + 100.0001 delta[1,0,70.0] >= 70.0001
 contribution_weight[188]: - w[0] + contribution[1,0,70.0] <= 0
 contribution_indicator[188]: - delta[1,0,70.0] + contribution[1,0,70.0]
   <= 0
 contribution_lower[188]: - w[0] - delta[1,0,70.0] + contribution[1,0,70.0]
   >= -1
 criterion_pass[189]: b[1,0] + 100.0001 delta[1,0,71.0] <= 171.0001
 criterion_fail[189]: b[1,0] + 100.0001 delta[1,0,71.0] >= 71.0001
 contribution_weight[189]: - w[0] + contribution[1,0,71.0] <= 0
 contribution_indicator[189]: - delta[1,0,71.0] + contribution[1,0,71.0]
   <= 0
 contribution_lower[189]: - w[0] - delta[1,0,71.0] + contribution[1,0,71.0]
   >= -1
 criterion_pass[190]: b[1,0] + 100.0001 delta[1,0,73.0] <= 173.0001
 criterion_fail[190]: b[1,0] + 100.0001 delta[1,0,73.0] >= 73.0001
 contribution_weight[190]: - w[0] + contribution[1,0,73.0] <= 0
 contribution_indicator[190]: - delta[1,0,73.0] + contribution[1,0,73.0]
   <= 0
 contribution_lower[190]: - w[0] - delta[1,0,73.0] + contribution[1,0,73.0]
   >= -1
 criterion_pass[191]: b[1,0] + 100.0001 delta[1,0,83.0] <= 183.0001
 criterion_fail[191]: b[1,0] + 100.0001 delta[1,0,83.0] >= 83.0001
 contribution_weight[191]: - w[0] + contribution[1,0,83.0] <= 0
 contribution_indicator[191]: - delta[1,0,83.0] + contribution[1,0,83.0]
   <= 0
 contribution_lower[191]: - w[0] - delta[1,0,83.0] + contribution[1,0,83.0]
   >= -1
 criterion_pass[192]: b[1,0] + 100.0001 delta[1,0,85.0] <= 185.0001
 criterion_fail[192]: b[1,0] + 100.0001 delta[1,0,85.0] >= 85.0001
 contribution_weight[192]: - w[0] + contribution[1,0,85.0] <= 0
 contribution_indicator[192]: - delta[1,0,85.0] + contribution[1,0,85.0]
   <= 0
 contribution_lower[192]: - w[0] - delta[1,0,85.0] + contribution[1,0,85.0]
   >= -1
 criterion_pass[193]: b[1,0] + 100.0001 delta[1,0,86.0] <= 186.0001
 criterion_fail[193]: b[1,0] + 100.0001 delta[1,0,86.0] >= 86.0001
 contribution_weight[193]: - w[0] + contribution[1,0,86.0] <= 0
 contribution_indicator[193]: - delta[1,0,86.0] + contribution[1,0,86.0]
   <= 0
 contribution_lower[193]: - w[0] - delta[1,0,86.0] + contribution[1,0,86.0]
   >= -1
 criterion_pass[194]: b[1,0] + 100.0001 delta[1,0,91.0] <= 191.0001
 criterion_fail[194]: b[1,0] + 100.0001 delta[1,0,91.0] >= 91.0001
 contribution_weight[194]: - w[0] + contribution[1,0,91.0] <= 0
 contribution_indicator[194]: - delta[1,0,91.0] + contribution[1,0,91.0]
   <= 0
 contribution_lower[194]: - w[0] - delta[1,0,91.0] + contribution[1,0,91.0]
   >= -1
 criterion_pass[195]: b[1,0] + 100.0001 delta[1,0,92.0] <= 192.0001
 criterion_fail[195]: b[1,0] + 100.0001 delta[1,0,92.0] >= 92.0001
 contribution_weight[195]: - w[0] + contribution[1,0,92.0] <= 0
 contribution_indicator[195]: - delta[1,0,92.0] + contribution[1,0,92.0]
   <= 0
 contribution_lower[195]: - w[0] - delta[1,0,92.0] + contribution[1,0,92.0]
   >= -1
 criterion_pass[196]: b[1,0] + 100.0001 delta[1,0,93.0] <= 193.0001
 criterion_fail[196]: b[1,0] + 100.0001 delta[1,0,93.0] >= 93.0001
 contribution_weight[196]: - w[0] + contribution[1,0,93.0] <= 0
 contribution_indicator[196]: - delta[1,0,93.0] + contribution[1,0,93.0]
   <= 0
 contribution_lower[196]: - w[0] - delta[1,0,93.0] + contribution[1,0,93.0]
   >= -1
 criterion_pass[197]: b[1,0] + 100.0001 delta[1,0,95.0] <= 195.0001
 criterion_fail[197]: b[1,0] + 100.0001 delta[1,0,95.0] >= 95.0001
 contribution_weight[197]: - w[0] + contribution[1,0,95.0] <= 0
 contribution_indicator[197]: - delta[1,0,95.0] + contribution[1,0,95.0]
   <= 0
 contribution_lower[197]: - w[0] - delta[1,0,95.0] + contribution[1,0,95.0]
   >= -1
 criterion_pass[198]: b[1,0] + 100.0001 delta[1,0,96.0] <= 196.0001
 criterion_fail[198]: b[1,0] + 100.0001 delta[1,0,96.0] >= 96.0001
 contribution_weight[198]: - w[0] + contribution[1,0,96.0] <= 0
 contribution_indicator[198]: - delta[1,0,96.0] + contribution[1,0,96.0]
   <= 0
 contribution_lower[198]: - w[0] - delta[1,0,96.0] + contribution[1,0,96.0]
   >= -1
 criterion_pass[199]: b[1,0] + 100.0001 delta[1,0,99.0] <= 199.0001
 criterion_fail[199]: b[1,0] + 100.0001 delta[1,0,99.0] >= 99.0001
 contribution_weight[199]: - w[0] + contribution[1,0,99.0] <= 0
 contribution_indicator[199]: - delta[1,0,99.0] + contribution[1,0,99.0]
   <= 0
 contribution_lower[199]: - w[0] - delta[1,0,99.0] + contribution[1,0,99.0]
   >= -1
 criterion_pass[200]: b[1,1] + 100.0001 delta[1,1,5.0] <= 105.0001
 criterion_fail[200]: b[1,1] + 100.0001 delta[1,1,5.0] >= 5.0001
 contribution_weight[200]: - w[1] + contribution[1,1,5.0] <= 0
 contribution_indicator[200]: - delta[1,1,5.0] + contribution[1,1,5.0]
   <= 0
 contribution_lower[200]: - w[1] - delta[1,1,5.0] + contribution[1,1,5.0]
   >= -1
 criterion_pass[201]: b[1,1] + 100.0001 delta[1,1,6.0] <= 106.0001
 criterion_fail[201]: b[1,1] + 100.0001 delta[1,1,6.0] >= 6.0001
 contribution_weight[201]: - w[1] + contribution[1,1,6.0] <= 0
 contribution_indicator[201]: - delta[1,1,6.0] + contribution[1,1,6.0]
   <= 0
 contribution_lower[201]: - w[1] - delta[1,1,6.0] + contribution[1,1,6.0]
   >= -1
 criterion_pass[202]: b[1,1] + 100.0001 delta[1,1,8.0] <= 108.0001
 criterion_fail[202]: b[1,1] + 100.0001 delta[1,1,8.0] >= 8.0001
 contribution_weight[202]: - w[1] + contribution[1,1,8.0] <= 0
 contribution_indicator[202]: - delta[1,1,8.0] + contribution[1,1,8.0]
   <= 0
 contribution_lower[202]: - w[1] - delta[1,1,8.0] + contribution[1,1,8.0]
   >= -1
 criterion_pass[203]: b[1,1] + 100.0001 delta[1,1,17.0] <= 117.0001
 criterion_fail[203]: b[1,1] + 100.0001 delta[1,1,17.0] >= 17.0001
 contribution_weight[203]: - w[1] + contribution[1,1,17.0] <= 0
 contribution_indicator[203]: - delta[1,1,17.0] + contribution[1,1,17.0]
   <= 0
 contribution_lower[203]: - w[1] - delta[1,1,17.0] + contribution[1,1,17.0]
   >= -1
 criterion_pass[204]: b[1,1] + 100.0001 delta[1,1,36.0] <= 136.0001
 criterion_fail[204]: b[1,1] + 100.0001 delta[1,1,36.0] >= 36.0001
 contribution_weight[204]: - w[1] + contribution[1,1,36.0] <= 0
 contribution_indicator[204]: - delta[1,1,36.0] + contribution[1,1,36.0]
   <= 0
 contribution_lower[204]: - w[1] - delta[1,1,36.0] + contribution[1,1,36.0]
   >= -1
 criterion_pass[205]: b[1,1] + 100.0001 delta[1,1,38.0] <= 138.0001
 criterion_fail[205]: b[1,1] + 100.0001 delta[1,1,38.0] >= 38.0001
 contribution_weight[205]: - w[1] + contribution[1,1,38.0] <= 0
 contribution_indicator[205]: - delta[1,1,38.0] + contribution[1,1,38.0]
   <= 0
 contribution_lower[205]: - w[1] - delta[1,1,38.0] + contribution[1,1,38.0]
   >= -1
 criterion_pass[206]: b[1,1] + 100.0001 delta[1,1,41.0] <= 141.0001
 criterion_fail[206]: b[1,1] + 100.0001 delta[1,1,41.0] >= 41.0001
 contribution_weight[206]: - w[1] + contribution[1,1,41.0] <= 0
 contribution_indicator[206]: - delta[1,1,41.0] + contribution[1,1,41.0]
   <= 0
 contribution_lower[206]: - w[1] - delta[1,1,41.0] + contribution[1,1,41.0]
   >= -1
 criterion_pass[207]: b[1,1] + 100.0001 delta[1,1,46.0] <= 146.0001
 criterion_fail[207]: b[1,1] + 100.0001 delta[1,1,46.0] >= 46.0001
 contribution_weight[207]: - w[1] + contribution[1,1,46.0] <= 0
 contribution_indicator[207]: - delta[1,1,46.0] + contribution[1,1,46.0]
   <= 0
 contribution_lower[207]: - w[1] - delta[1,1,46.0] + contribution[1,1,46.0]
   >= -1
 criterion_pass[208]: b[1,1] + 100.0001 delta[1,1,48.0] <= 148.0001
 criterion_fail[208]: b[1,1] + 100.0001 delta[1,1,48.0] >= 48.0001
 contribution_weight[208]: - w[1] + contribution[1,1,48.0] <= 0
 contribution_indicator[208]: - delta[1,1,48.0] + contribution[1,1,48.0]
   <= 0
 contribution_lower[208]: - w[1] - delta[1,1,48.0] + contribution[1,1,48.0]
   >= -1
 criterion_pass[209]: b[1,1] + 100.0001 delta[1,1,52.0] <= 152.0001
 criterion_fail[209]: b[1,1] + 100.0001 delta[1,1,52.0] >= 52.0001
 contribution_weight[209]: - w[1] + contribution[1,1,52.0] <= 0
 contribution_indicator[209]: - delta[1,1,52.0] + contribution[1,1,52.0]
   <= 0
 contribution_lower[209]: - w[1] - delta[1,1,52.0] + contribution[1,1,52.0]
   >= -1
 criterion_pass[210]: b[1,1] + 100.0001 delta[1,1,53.0] <= 153.0001
 criterion_fail[210]: b[1,1] + 100.0001 delta[1,1,53.0] >= 53.0001
 contribution_weight[210]: - w[1] + contribution[1,1,53.0] <= 0
 contribution_indicator[210]: - delta[1,1,53.0] + contribution[1,1,53.0]
   <= 0
 contribution_lower[210]: - w[1] - delta[1,1,53.0] + contribution[1,1,53.0]
   >= -1
 criterion_pass[211]: b[1,1] + 100.0001 delta[1,1,54.0] <= 154.0001
 criterion_fail[211]: b[1,1] + 100.0001 delta[1,1,54.0] >= 54.0001
 contribution_weight[211]: - w[1] + contribution[1,1,54.0] <= 0
 contribution_indicator[211]: - delta[1,1,54.0] + contribution[1,1,54.0]
   <= 0
 contribution_lower[211]: - w[1] - delta[1,1,54.0] + contribution[1,1,54.0]
   >= -1
 criterion_pass[212]: b[1,1] + 100.0001 delta[1,1,55.0] <= 155.0001
 criterion_fail[212]: b[1,1] + 100.0001 delta[1,1,55.0] >= 55.0001
 contribution_weight[212]: - w[1] + contribution[1,1,55.0] <= 0
 contribution_indicator[212]: - delta[1,1,55.0] + contribution[1,1,55.0]
   <= 0
 contribution_lower[212]: - w[1] - delta[1,1,55.0] + contribution[1,1,55.0]
   >= -1
 criterion_pass[213]: b[1,1] + 100.0001 delta[1,1,56.0] <= 156.0001
 criterion_fail[213]: b[1,1] + 100.0001 delta[1,1,56.0] >= 56.0001
 contribution_weight[213]: - w[1] + contribution[1,1,56.0] <= 0
 contribution_indicator[213]: - delta[1,1,56.0] + contribution[1,1,56.0]
   <= 0
 contribution_lower[213]: - w[1] - delta[1,1,56.0] + contribution[1,1,56.0]
   >= -1
 criterion_pass[214]: b[1,1] + 100.0001 delta[1,1,57.0] <= 157.0001
 criterion_fail[214]: b[1,1] + 100.0001 delta[1,1,57.0] >= 57.0001
 contribution_weight[214]: - w[1] + contribution[1,1,57.0] <= 0
 contribution_indicator[214]: - delta[1,1,57.0] + contribution[1,1,57.0]
   <= 0
 contribution_lower[214]: - w[1] - delta[1,1,57.0] + contribution[1,1,57.0]
   >= -1
 criterion_pass[215]: b[1,1] + 100.0001 delta[1,1,61.0] <= 161.0001
 criterion_fail[215]: b[1,1] + 100.0001 delta[1,1,61.0] >= 61.0001
 contribution_weight[215]: - w[1] + contribution[1,1,61.0] <= 0
 contribution_indicator[215]: - delta[1,1,61.0] + contribution[1,1,61.0]
   <= 0
 contribution_lower[215]: - w[1] - delta[1,1,61.0] + contribution[1,1,61.0]
   >= -1
 criterion_pass[216]: b[1,1] + 100.0001 delta[1,1,63.0] <= 163.0001
 criterion_fail[216]: b[1,1] + 100.0001 delta[1,1,63.0] >= 63.0001
 contribution_weight[216]: - w[1] + contribution[1,1,63.0] <= 0
 contribution_indicator[216]: - delta[1,1,63.0] + contribution[1,1,63.0]
   <= 0
 contribution_lower[216]: - w[1] - delta[1,1,63.0] + contribution[1,1,63.0]
   >= -1
 criterion_pass[217]: b[1,1] + 100.0001 delta[1,1,65.0] <= 165.0001
 criterion_fail[217]: b[1,1] + 100.0001 delta[1,1,65.0] >= 65.0001
 contribution_weight[217]: - w[1] + contribution[1,1,65.0] <= 0
 contribution_indicator[217]: - delta[1,1,65.0] + contribution[1,1,65.0]
   <= 0
 contribution_lower[217]: - w[1] - delta[1,1,65.0] + contribution[1,1,65.0]
   >= -1
 criterion_pass[218]: b[1,1] + 100.0001 delta[1,1,68.0] <= 168.0001
 criterion_fail[218]: b[1,1] + 100.0001 delta[1,1,68.0] >= 68.0001
 contribution_weight[218]: - w[1] + contribution[1,1,68.0] <= 0
 contribution_indicator[218]: - delta[1,1,68.0] + contribution[1,1,68.0]
   <= 0
 contribution_lower[218]: - w[1] - delta[1,1,68.0] + contribution[1,1,68.0]
   >= -1
 criterion_pass[219]: b[1,1] + 100.0001 delta[1,1,72.0] <= 172.0001
 criterion_fail[219]: b[1,1] + 100.0001 delta[1,1,72.0] >= 72.0001
 contribution_weight[219]: - w[1] + contribution[1,1,72.0] <= 0
 contribution_indicator[219]: - delta[1,1,72.0] + contribution[1,1,72.0]
   <= 0
 contribution_lower[219]: - w[1] - delta[1,1,72.0] + contribution[1,1,72.0]
   >= -1
 criterion_pass[220]: b[1,1] + 100.0001 delta[1,1,76.0] <= 176.0001
 criterion_fail[220]: b[1,1] + 100.0001 delta[1,1,76.0] >= 76.0001
 contribution_weight[220]: - w[1] + contribution[1,1,76.0] <= 0
 contribution_indicator[220]: - delta[1,1,76.0] + contribution[1,1,76.0]
   <= 0
 contribution_lower[220]: - w[1] - delta[1,1,76.0] + contribution[1,1,76.0]
   >= -1
 criterion_pass[221]: b[1,1] + 100.0001 delta[1,1,80.0] <= 180.0001
 criterion_fail[221]: b[1,1] + 100.0001 delta[1,1,80.0] >= 80.0001
 contribution_weight[221]: - w[1] + contribution[1,1,80.0] <= 0
 contribution_indicator[221]: - delta[1,1,80.0] + contribution[1,1,80.0]
   <= 0
 contribution_lower[221]: - w[1] - delta[1,1,80.0] + contribution[1,1,80.0]
   >= -1
 criterion_pass[222]: b[1,1] + 100.0001 delta[1,1,81.0] <= 181.0001
 criterion_fail[222]: b[1,1] + 100.0001 delta[1,1,81.0] >= 81.0001
 contribution_weight[222]: - w[1] + contribution[1,1,81.0] <= 0
 contribution_indicator[222]: - delta[1,1,81.0] + contribution[1,1,81.0]
   <= 0
 contribution_lower[222]: - w[1] - delta[1,1,81.0] + contribution[1,1,81.0]
   >= -1
 criterion_pass[223]: b[1,1] + 100.0001 delta[1,1,82.0] <= 182.0001
 criterion_fail[223]: b[1,1] + 100.0001 delta[1,1,82.0] >= 82.0001
 contribution_weight[223]: - w[1] + contribution[1,1,82.0] <= 0
 contribution_indicator[223]: - delta[1,1,82.0] + contribution[1,1,82.0]
   <= 0
 contribution_lower[223]: - w[1] - delta[1,1,82.0] + contribution[1,1,82.0]
   >= -1
 criterion_pass[224]: b[1,1] + 100.0001 delta[1,1,84.0] <= 184.0001
 criterion_fail[224]: b[1,1] + 100.0001 delta[1,1,84.0] >= 84.0001
 contribution_weight[224]: - w[1] + contribution[1,1,84.0] <= 0
 contribution_indicator[224]: - delta[1,1,84.0] + contribution[1,1,84.0]
   <= 0
 contribution_lower[224]: - w[1] - delta[1,1,84.0] + contribution[1,1,84.0]
   >= -1
 criterion_pass[225]: b[1,1] + 100.0001 delta[1,1,86.0] <= 186.0001
 criterion_fail[225]: b[1,1] + 100.0001 delta[1,1,86.0] >= 86.0001
 contribution_weight[225]: - w[1] + contribution[1,1,86.0] <= 0
 contribution_indicator[225]: - delta[1,1,86.0] + contribution[1,1,86.0]
   <= 0
 contribution_lower[225]: - w[1] - delta[1,1,86.0] + contribution[1,1,86.0]
   >= -1
 criterion_pass[226]: b[1,1] + 100.0001 delta[1,1,87.0] <= 187.0001
 criterion_fail[226]: b[1,1] + 100.0001 delta[1,1,87.0] >= 87.0001
 contribution_weight[226]: - w[1] + contribution[1,1,87.0] <= 0
 contribution_indicator[226]: - delta[1,1,87.0] + contribution[1,1,87.0]
   <= 0
 contribution_lower[226]: - w[1] - delta[1,1,87.0] + contribution[1,1,87.0]
   >= -1
 criterion_pass[227]: b[1,1] + 100.0001 delta[1,1,91.0] <= 191.0001
 criterion_fail[227]: b[1,1] + 100.0001 delta[1,1,91.0] >= 91.0001
 contribution_weight[227]: - w[1] + contribution[1,1,91.0] <= 0
 contribution_indicator[227]: - delta[1,1,91.0] + contribution[1,1,91.0]
   <= 0
 contribution_lower[227]: - w[1] - delta[1,1,91.0] + contribution[1,1,91.0]
   >= -1
 criterion_pass[228]: b[1,1] + 100.0001 delta[1,1,92.0] <= 192.0001
 criterion_fail[228]: b[1,1] + 100.0001 delta[1,1,92.0] >= 92.0001
 contribution_weight[228]: - w[1] + contribution[1,1,92.0] <= 0
 contribution_indicator[228]: - delta[1,1,92.0] + contribution[1,1,92.0]
   <= 0
 contribution_lower[228]: - w[1] - delta[1,1,92.0] + contribution[1,1,92.0]
   >= -1
 criterion_pass[229]: b[1,1] + 100.0001 delta[1,1,94.0] <= 194.0001
 criterion_fail[229]: b[1,1] + 100.0001 delta[1,1,94.0] >= 94.0001
 contribution_weight[229]: - w[1] + contribution[1,1,94.0] <= 0
 contribution_indicator[229]: - delta[1,1,94.0] + contribution[1,1,94.0]
   <= 0
 contribution_lower[229]: - w[1] - delta[1,1,94.0] + contribution[1,1,94.0]
   >= -1
 criterion_pass[230]: b[1,1] + 100.0001 delta[1,1,95.0] <= 195.0001
 criterion_fail[230]: b[1,1] + 100.0001 delta[1,1,95.0] >= 95.0001
 contribution_weight[230]: - w[1] + contribution[1,1,95.0] <= 0
 contribution_indicator[230]: - delta[1,1,95.0] + contribution[1,1,95.0]
   <= 0
 contribution_lower[230]: - w[1] - delta[1,1,95.0] + contribution[1,1,95.0]
   >= -1
 criterion_pass[231]: b[1,1] + 100.0001 delta[1,1,96.0] <= 196.0001
 criterion_fail[231]: b[1,1] + 100.0001 delta[1,1,96.0] >= 96.0001
 contribution_weight[231]: - w[1] + contribution[1,1,96.0] <= 0
 contribution_indicator[231]: - delta[1,1,96.0] + contribution[1,1,96.0]
   <= 0
 contribution_lower[231]: - w[1] - delta[1,1,96.0] + contribution[1,1,96.0]
   >= -1
 criterion_pass[232]: b[1,1] + 100.0001 delta[1,1,100.0] <= 200.0001
 criterion_fail[232]: b[1,1] + 100.0001 delta[1,1,100.0] >= 100.0001
 contribution_weight[232]: - w[1] + contribution[1,1,100.0] <= 0
 contribution_indicator[232]: - delta[1,1,100.0] + contribution[1,1,100.0]
   <= 0
 contribution_lower[232]: - w[1] - delta[1,1,100.0]
   + contribution[1,1,100.0] >= -1
 criterion_pass[233]: b[1,2] + 100.0001 delta[1,2,3.0] <= 103.0001
 criterion_fail[233]: b[1,2] + 100.0001 delta[1,2,3.0] >= 3.0001
 contribution_weight[233]: - w[2] + contribution[1,2,3.0] <= 0
 contribution_indicator[233]: - delta[1,2,3.0] + contribution[1,2,3.0]
   <= 0
 contribution_lower[233]: - w[2] - delta[1,2,3.0] + contribution[1,2,3.0]
   >= -1
 criterion_pass[234]: b[1,2] + 100.0001 delta[1,2,4.0] <= 104.0001
 criterion_fail[234]: b[1,2] + 100.0001 delta[1,2,4.0] >= 4.0001
 contribution_weight[234]: - w[2] + contribution[1,2,4.0] <= 0
 contribution_indicator[234]: - delta[1,2,4.0] + contribution[1,2,4.0]
   <= 0
 contribution_lower[234]: - w[2] - delta[1,2,4.0] + contribution[1,2,4.0]
   >= -1
 criterion_pass[235]: b[1,2] + 100.0001 delta[1,2,7.0] <= 107.0001
 criterion_fail[235]: b[1,2] + 100.0001 delta[1,2,7.0] >= 7.0001
 contribution_weight[235]: - w[2] + contribution[1,2,7.0] <= 0
 contribution_indicator[235]: - delta[1,2,7.0] + contribution[1,2,7.0]
   <= 0
 contribution_lower[235]: - w[2] - delta[1,2,7.0] + contribution[1,2,7.0]
   >= -1
 criterion_pass[236]: b[1,2] + 100.0001 delta[1,2,9.0] <= 109.0001
 criterion_fail[236]: b[1,2] + 100.0001 delta[1,2,9.0] >= 9.0001
 contribution_weight[236]: - w[2] + contribution[1,2,9.0] <= 0
 contribution_indicator[236]: - delta[1,2,9.0] + contribution[1,2,9.0]
   <= 0
 contribution_lower[236]: - w[2] - delta[1,2,9.0] + contribution[1,2,9.0]
   >= -1
 criterion_pass[237]: b[1,2] + 100.0001 delta[1,2,12.0] <= 112.0001
 criterion_fail[237]: b[1,2] + 100.0001 delta[1,2,12.0] >= 12.0001
 contribution_weight[237]: - w[2] + contribution[1,2,12.0] <= 0
 contribution_indicator[237]: - delta[1,2,12.0] + contribution[1,2,12.0]
   <= 0
 contribution_lower[237]: - w[2] - delta[1,2,12.0] + contribution[1,2,12.0]
   >= -1
 criterion_pass[238]: b[1,2] + 100.0001 delta[1,2,13.0] <= 113.0001
 criterion_fail[238]: b[1,2] + 100.0001 delta[1,2,13.0] >= 13.0001
 contribution_weight[238]: - w[2] + contribution[1,2,13.0] <= 0
 contribution_indicator[238]: - delta[1,2,13.0] + contribution[1,2,13.0]
   <= 0
 contribution_lower[238]: - w[2] - delta[1,2,13.0] + contribution[1,2,13.0]
   >= -1
 criterion_pass[239]: b[1,2] + 100.0001 delta[1,2,14.0] <= 114.0001
 criterion_fail[239]: b[1,2] + 100.0001 delta[1,2,14.0] >= 14.0001
 contribution_weight[239]: - w[2] + contribution[1,2,14.0] <= 0
 contribution_indicator[239]: - delta[1,2,14.0] + contribution[1,2,14.0]
   <= 0
 contribution_lower[239]: - w[2] - delta[1,2,14.0] + contribution[1,2,14.0]
   >= -1
 criterion_pass[240]: b[1,2] + 100.0001 delta[1,2,26.0] <= 126.0001
 criterion_fail[240]: b[1,2] + 100.0001 delta[1,2,26.0] >= 26.0001
 contribution_weight[240]: - w[2] + contribution[1,2,26.0] <= 0
 contribution_indicator[240]: - delta[1,2,26.0] + contribution[1,2,26.0]
   <= 0
 contribution_lower[240]: - w[2] - delta[1,2,26.0] + contribution[1,2,26.0]
   >= -1
 criterion_pass[241]: b[1,2] + 100.0001 delta[1,2,27.0] <= 127.0001
 criterion_fail[241]: b[1,2] + 100.0001 delta[1,2,27.0] >= 27.0001
 contribution_weight[241]: - w[2] + contribution[1,2,27.0] <= 0
 contribution_indicator[241]: - delta[1,2,27.0] + contribution[1,2,27.0]
   <= 0
 contribution_lower[241]: - w[2] - delta[1,2,27.0] + contribution[1,2,27.0]
   >= -1
 criterion_pass[242]: b[1,2] + 100.0001 delta[1,2,28.0] <= 128.0001
 criterion_fail[242]: b[1,2] + 100.0001 delta[1,2,28.0] >= 28.0001
 contribution_weight[242]: - w[2] + contribution[1,2,28.0] <= 0
 contribution_indicator[242]: - delta[1,2,28.0] + contribution[1,2,28.0]
   <= 0
 contribution_lower[242]: - w[2] - delta[1,2,28.0] + contribution[1,2,28.0]
   >= -1
 criterion_pass[243]: b[1,2] + 100.0001 delta[1,2,29.0] <= 129.0001
 criterion_fail[243]: b[1,2] + 100.0001 delta[1,2,29.0] >= 29.0001
 contribution_weight[243]: - w[2] + contribution[1,2,29.0] <= 0
 contribution_indicator[243]: - delta[1,2,29.0] + contribution[1,2,29.0]
   <= 0
 contribution_lower[243]: - w[2] - delta[1,2,29.0] + contribution[1,2,29.0]
   >= -1
 criterion_pass[244]: b[1,2] + 100.0001 delta[1,2,37.0] <= 137.0001
 criterion_fail[244]: b[1,2] + 100.0001 delta[1,2,37.0] >= 37.0001
 contribution_weight[244]: - w[2] + contribution[1,2,37.0] <= 0
 contribution_indicator[244]: - delta[1,2,37.0] + contribution[1,2,37.0]
   <= 0
 contribution_lower[244]: - w[2] - delta[1,2,37.0] + contribution[1,2,37.0]
   >= -1
 criterion_pass[245]: b[1,2] + 100.0001 delta[1,2,50.0] <= 150.0001
 criterion_fail[245]: b[1,2] + 100.0001 delta[1,2,50.0] >= 50.0001
 contribution_weight[245]: - w[2] + contribution[1,2,50.0] <= 0
 contribution_indicator[245]: - delta[1,2,50.0] + contribution[1,2,50.0]
   <= 0
 contribution_lower[245]: - w[2] - delta[1,2,50.0] + contribution[1,2,50.0]
   >= -1
 criterion_pass[246]: b[1,2] + 100.0001 delta[1,2,56.0] <= 156.0001
 criterion_fail[246]: b[1,2] + 100.0001 delta[1,2,56.0] >= 56.0001
 contribution_weight[246]: - w[2] + contribution[1,2,56.0] <= 0
 contribution_indicator[246]: - delta[1,2,56.0] + contribution[1,2,56.0]
   <= 0
 contribution_lower[246]: - w[2] - delta[1,2,56.0] + contribution[1,2,56.0]
   >= -1
 criterion_pass[247]: b[1,2] + 100.0001 delta[1,2,57.0] <= 157.0001
 criterion_fail[247]: b[1,2] + 100.0001 delta[1,2,57.0] >= 57.0001
 contribution_weight[247]: - w[2] + contribution[1,2,57.0] <= 0
 contribution_indicator[247]: - delta[1,2,57.0] + contribution[1,2,57.0]
   <= 0
 contribution_lower[247]: - w[2] - delta[1,2,57.0] + contribution[1,2,57.0]
   >= -1
 criterion_pass[248]: b[1,2] + 100.0001 delta[1,2,60.0] <= 160.0001
 criterion_fail[248]: b[1,2] + 100.0001 delta[1,2,60.0] >= 60.0001
 contribution_weight[248]: - w[2] + contribution[1,2,60.0] <= 0
 contribution_indicator[248]: - delta[1,2,60.0] + contribution[1,2,60.0]
   <= 0
 contribution_lower[248]: - w[2] - delta[1,2,60.0] + contribution[1,2,60.0]
   >= -1
 criterion_pass[249]: b[1,2] + 100.0001 delta[1,2,61.0] <= 161.0001
 criterion_fail[249]: b[1,2] + 100.0001 delta[1,2,61.0] >= 61.0001
 contribution_weight[249]: - w[2] + contribution[1,2,61.0] <= 0
 contribution_indicator[249]: - delta[1,2,61.0] + contribution[1,2,61.0]
   <= 0
 contribution_lower[249]: - w[2] - delta[1,2,61.0] + contribution[1,2,61.0]
   >= -1
 criterion_pass[250]: b[1,2] + 100.0001 delta[1,2,66.0] <= 166.0001
 criterion_fail[250]: b[1,2] + 100.0001 delta[1,2,66.0] >= 66.0001
 contribution_weight[250]: - w[2] + contribution[1,2,66.0] <= 0
 contribution_indicator[250]: - delta[1,2,66.0] + contribution[1,2,66.0]
   <= 0
 contribution_lower[250]: - w[2] - delta[1,2,66.0] + contribution[1,2,66.0]
   >= -1
 criterion_pass[251]: b[1,2] + 100.0001 delta[1,2,69.0] <= 169.0001
 criterion_fail[251]: b[1,2] + 100.0001 delta[1,2,69.0] >= 69.0001
 contribution_weight[251]: - w[2] + contribution[1,2,69.0] <= 0
 contribution_indicator[251]: - delta[1,2,69.0] + contribution[1,2,69.0]
   <= 0
 contribution_lower[251]: - w[2] - delta[1,2,69.0] + contribution[1,2,69.0]
   >= -1
 criterion_pass[252]: b[1,2] + 100.0001 delta[1,2,73.0] <= 173.0001
 criterion_fail[252]: b[1,2] + 100.0001 delta[1,2,73.0] >= 73.0001
 contribution_weight[252]: - w[2] + contribution[1,2,73.0] <= 0
 contribution_indicator[252]: - delta[1,2,73.0] + contribution[1,2,73.0]
   <= 0
 contribution_lower[252]: - w[2] - delta[1,2,73.0] + contribution[1,2,73.0]
   >= -1
 criterion_pass[253]: b[1,2] + 100.0001 delta[1,2,76.0] <= 176.0001
 criterion_fail[253]: b[1,2] + 100.0001 delta[1,2,76.0] >= 76.0001
 contribution_weight[253]: - w[2] + contribution[1,2,76.0] <= 0
 contribution_indicator[253]: - delta[1,2,76.0] + contribution[1,2,76.0]
   <= 0
 contribution_lower[253]: - w[2] - delta[1,2,76.0] + contribution[1,2,76.0]
   >= -1
 criterion_pass[254]: b[1,2] + 100.0001 delta[1,2,77.0] <= 177.0001
 criterion_fail[254]: b[1,2] + 100.0001 delta[1,2,77.0] >= 77.0001
 contribution_weight[254]: - w[2] + contribution[1,2,77.0] <= 0
 contribution_indicator[254]: - delta[1,2,77.0] + contribution[1,2,77.0]
   <= 0
 contribution_lower[254]: - w[2] - delta[1,2,77.0] + contribution[1,2,77.0]
   >= -1
 criterion_pass[255]: b[1,2] + 100.0001 delta[1,2,84.0] <= 184.0001
 criterion_fail[255]: b[1,2] + 100.0001 delta[1,2,84.0] >= 84.0001
 contribution_weight[255]: - w[2] + contribution[1,2,84.0] <= 0
 contribution_indicator[255]: - delta[1,2,84.0] + contribution[1,2,84.0]
   <= 0
 contribution_lower[255]: - w[2] - delta[1,2,84.0] + contribution[1,2,84.0]
   >= -1
 criterion_pass[256]: b[1,2] + 100.0001 delta[1,2,86.0] <= 186.0001
 criterion_fail[256]: b[1,2] + 100.0001 delta[1,2,86.0] >= 86.0001
 contribution_weight[256]: - w[2] + contribution[1,2,86.0] <= 0
 contribution_indicator[256]: - delta[1,2,86.0] + contribution[1,2,86.0]
   <= 0
 contribution_lower[256]: - w[2] - delta[1,2,86.0] + contribution[1,2,86.0]
   >= -1
 criterion_pass[257]: b[1,2] + 100.0001 delta[1,2,87.0] <= 187.0001
 criterion_fail[257]: b[1,2] + 100.0001 delta[1,2,87.0] >= 87.0001
 contribution_weight[257]: - w[2] + contribution[1,2,87.0] <= 0
 contribution_indicator[257]: - delta[1,2,87.0] + contribution[1,2,87.0]
   <= 0
 contribution_lower[257]: - w[2] - delta[1,2,87.0] + contribution[1,2,87.0]
   >= -1
 criterion_pass[258]: b[1,2] + 100.0001 delta[1,2,88.0] <= 188.0001
 criterion_fail[258]: b[1,2] + 100.0001 delta[1,2,88.0] >= 88.0001
 contribution_weight[258]: - w[2] + contribution[1,2,88.0] <= 0
 contribution_indicator[258]: - delta[1,2,88.0] + contribution[1,2,88.0]
   <= 0
 contribution_lower[258]: - w[2] - delta[1,2,88.0] + contribution[1,2,88.0]
   >= -1
 criterion_pass[259]: b[1,2] + 100.0001 delta[1,2,90.0] <= 190.0001
 criterion_fail[259]: b[1,2] + 100.0001 delta[1,2,90.0] >= 90.0001
 contribution_weight[259]: - w[2] + contribution[1,2,90.0] <= 0
 contribution_indicator[259]: - delta[1,2,90.0] + contribution[1,2,90.0]
   <= 0
 contribution_lower[259]: - w[2] - delta[1,2,90.0] + contribution[1,2,90.0]
   >= -1
 criterion_pass[260]: b[1,2] + 100.0001 delta[1,2,91.0] <= 191.0001
 criterion_fail[260]: b[1,2] + 100.0001 delta[1,2,91.0] >= 91.0001
 contribution_weight[260]: - w[2] + contribution[1,2,91.0] <= 0
 contribution_indicator[260]: - delta[1,2,91.0] + contribution[1,2,91.0]
   <= 0
 contribution_lower[260]: - w[2] - delta[1,2,91.0] + contribution[1,2,91.0]
   >= -1
 criterion_pass[261]: b[1,2] + 100.0001 delta[1,2,93.0] <= 193.0001
 criterion_fail[261]: b[1,2] + 100.0001 delta[1,2,93.0] >= 93.0001
 contribution_weight[261]: - w[2] + contribution[1,2,93.0] <= 0
 contribution_indicator[261]: - delta[1,2,93.0] + contribution[1,2,93.0]
   <= 0
 contribution_lower[261]: - w[2] - delta[1,2,93.0] + contribution[1,2,93.0]
   >= -1
 criterion_pass[262]: b[1,2] + 100.0001 delta[1,2,97.0] <= 197.0001
 criterion_fail[262]: b[1,2] + 100.0001 delta[1,2,97.0] >= 97.0001
 contribution_weight[262]: - w[2] + contribution[1,2,97.0] <= 0
 contribution_indicator[262]: - delta[1,2,97.0] + contribution[1,2,97.0]
   <= 0
 contribution_lower[262]: - w[2] - delta[1,2,97.0] + contribution[1,2,97.0]
   >= -1
 criterion_pass[263]: b[1,2] + 100.0001 delta[1,2,98.0] <= 198.0001
 criterion_fail[263]: b[1,2] + 100.0001 delta[1,2,98.0] >= 98.0001
 contribution_weight[263]: - w[2] + contribution[1,2,98.0] <= 0
 contribution_indicator[263]: - delta[1,2,98.0] + contribution[1,2,98.0]
   <= 0
 contribution_lower[263]: - w[2] - delta[1,2,98.0] + contribution[1,2,98.0]
   >= -1
 criterion_pass[264]: b[1,2] + 100.0001 delta[1,2,99.0] <= 199.0001
 criterion_fail[264]: b[1,2] + 100.0001 delta[1,2,99.0] >= 99.0001
 contribution_weight[264]: - w[2] + contribution[1,2,99.0] <= 0
 contribution_indicator[264]: - delta[1,2,99.0] + contribution[1,2,99.0]
   <= 0
 contribution_lower[264]: - w[2] - delta[1,2,99.0] + contribution[1,2,99.0]
   >= -1
 criterion_pass[265]: b[1,2] + 100.0001 delta[1,2,100.0] <= 200.0001
 criterion_fail[265]: b[1,2] + 100.0001 delta[1,2,100.0] >= 100.0001
 contribution_weight[265]: - w[2] + contribution[1,2,100.0] <= 0
 contribution_indicator[265]: - delta[1,2,100.0] + contribution[1,2,100.0]
   <= 0
 contribution_lower[265]: - w[2] - delta[1,2,100.0]
   + contribution[1,2,100.0] >= -1
 criterion_pass[266]: b[1,3] + 100.0001 delta[1,3,2.0] <= 102.0001
 criterion_fail[266]: b[1,3] + 100.0001 delta[1,3,2.0] >= 2.0001
 contribution_weight[266]: - w[3] + contribution[1,3,2.0] <= 0
 contribution_indicator[266]: - delta[1,3,2.0] + contribution[1,3,2.0]
   <= 0
 contribution_lower[266]: - w[3] - delta[1,3,2.0] + contribution[1,3,2.0]
   >= -1
 criterion_pass[267]: b[1,3] + 100.0001 delta[1,3,6.0] <= 106.0001
 criterion_fail[267]: b[1,3] + 100.0001 delta[1,3,6.0] >= 6.0001
 contribution_weight[267]: - w[3] + contribution[1,3,6.0] <= 0
 contribution_indicator[267]: - delta[1,3,6.0] + contribution[1,3,6.0]
   <= 0
 contribution_lower[267]: - w[3] - delta[1,3,6.0] + contribution[1,3,6.0]
   >= -1
 criterion_pass[268]: b[1,3] + 100.0001 delta[1,3,13.0] <= 113.0001
 criterion_fail[268]: b[1,3] + 100.0001 delta[1,3,13.0] >= 13.0001
 contribution_weight[268]: - w[3] + contribution[1,3,13.0] <= 0
 contribution_indicator[268]: - delta[1,3,13.0] + contribution[1,3,13.0]
   <= 0
 contribution_lower[268]: - w[3] - delta[1,3,13.0] + contribution[1,3,13.0]
   >= -1
 criterion_pass[269]: b[1,3] + 100.0001 delta[1,3,19.0] <= 119.0001
 criterion_fail[269]: b[1,3] + 100.0001 delta[1,3,19.0] >= 19.0001
 contribution_weight[269]: - w[3] + contribution[1,3,19.0] <= 0
 contribution_indicator[269]: - delta[1,3,19.0] + contribution[1,3,19.0]
   <= 0
 contribution_lower[269]: - w[3] - delta[1,3,19.0] + contribution[1,3,19.0]
   >= -1
 criterion_pass[270]: b[1,3] + 100.0001 delta[1,3,23.0] <= 123.0001
 criterion_fail[270]: b[1,3] + 100.0001 delta[1,3,23.0] >= 23.0001
 contribution_weight[270]: - w[3] + contribution[1,3,23.0] <= 0
 contribution_indicator[270]: - delta[1,3,23.0] + contribution[1,3,23.0]
   <= 0
 contribution_lower[270]: - w[3] - delta[1,3,23.0] + contribution[1,3,23.0]
   >= -1
 criterion_pass[271]: b[1,3] + 100.0001 delta[1,3,26.0] <= 126.0001
 criterion_fail[271]: b[1,3] + 100.0001 delta[1,3,26.0] >= 26.0001
 contribution_weight[271]: - w[3] + contribution[1,3,26.0] <= 0
 contribution_indicator[271]: - delta[1,3,26.0] + contribution[1,3,26.0]
   <= 0
 contribution_lower[271]: - w[3] - delta[1,3,26.0] + contribution[1,3,26.0]
   >= -1
 criterion_pass[272]: b[1,3] + 100.0001 delta[1,3,34.0] <= 134.0001
 criterion_fail[272]: b[1,3] + 100.0001 delta[1,3,34.0] >= 34.0001
 contribution_weight[272]: - w[3] + contribution[1,3,34.0] <= 0
 contribution_indicator[272]: - delta[1,3,34.0] + contribution[1,3,34.0]
   <= 0
 contribution_lower[272]: - w[3] - delta[1,3,34.0] + contribution[1,3,34.0]
   >= -1
 criterion_pass[273]: b[1,3] + 100.0001 delta[1,3,35.0] <= 135.0001
 criterion_fail[273]: b[1,3] + 100.0001 delta[1,3,35.0] >= 35.0001
 contribution_weight[273]: - w[3] + contribution[1,3,35.0] <= 0
 contribution_indicator[273]: - delta[1,3,35.0] + contribution[1,3,35.0]
   <= 0
 contribution_lower[273]: - w[3] - delta[1,3,35.0] + contribution[1,3,35.0]
   >= -1
 criterion_pass[274]: b[1,3] + 100.0001 delta[1,3,36.0] <= 136.0001
 criterion_fail[274]: b[1,3] + 100.0001 delta[1,3,36.0] >= 36.0001
 contribution_weight[274]: - w[3] + contribution[1,3,36.0] <= 0
 contribution_indicator[274]: - delta[1,3,36.0] + contribution[1,3,36.0]
   <= 0
 contribution_lower[274]: - w[3] - delta[1,3,36.0] + contribution[1,3,36.0]
   >= -1
 criterion_pass[275]: b[1,3] + 100.0001 delta[1,3,37.0] <= 137.0001
 criterion_fail[275]: b[1,3] + 100.0001 delta[1,3,37.0] >= 37.0001
 contribution_weight[275]: - w[3] + contribution[1,3,37.0] <= 0
 contribution_indicator[275]: - delta[1,3,37.0] + contribution[1,3,37.0]
   <= 0
 contribution_lower[275]: - w[3] - delta[1,3,37.0] + contribution[1,3,37.0]
   >= -1
 criterion_pass[276]: b[1,3] + 100.0001 delta[1,3,38.0] <= 138.0001
 criterion_fail[276]: b[1,3] + 100.0001 delta[1,3,38.0] >= 38.0001
 contribution_weight[276]: - w[3] + contribution[1,3,38.0] <= 0
 contribution_indicator[276]: - delta[1,3,38.0] + contribution[1,3,38.0]
   <= 0
 contribution_lower[276]: - w[3] - delta[1,3,38.0] + contribution[1,3,38.0]
   >= -1
 criterion_pass[277]: b[1,3] + 100.0001 delta[1,3,39.0] <= 139.0001
 criterion_fail[277]: b[1,3] + 100.0001 delta[1,3,39.0] >= 39.0001
 contribution_weight[277]: - w[3] + contribution[1,3,39.0] <= 0
 contribution_indicator[277]: - delta[1,3,39.0] + contribution[1,3,39.0]
   <= 0
 contribution_lower[277]: - w[3] - delta[1,3,39.0] + contribution[1,3,39.0]
   >= -1
 criterion_pass[278]: b[1,3] + 100.0001 delta[1,3,41.0] <= 141.0001
 criterion_fail[278]: b[1,3] + 100.0001 delta[1,3,41.0] >= 41.0001
 contribution_weight[278]: - w[3] + contribution[1,3,41.0] <= 0
 contribution_indicator[278]: - delta[1,3,41.0] + contribution[1,3,41.0]
   <= 0
 contribution_lower[278]: - w[3] - delta[1,3,41.0] + contribution[1,3,41.0]
   >= -1
 criterion_pass[279]: b[1,3] + 100.0001 delta[1,3,43.0] <= 143.0001
 criterion_fail[279]: b[1,3] + 100.0001 delta[1,3,43.0] >= 43.0001
 contribution_weight[279]: - w[3] + contribution[1,3,43.0] <= 0
 contribution_indicator[279]: - delta[1,3,43.0] + contribution[1,3,43.0]
   <= 0
 contribution_lower[279]: - w[3] - delta[1,3,43.0] + contribution[1,3,43.0]
   >= -1
 criterion_pass[280]: b[1,3] + 100.0001 delta[1,3,44.0] <= 144.0001
 criterion_fail[280]: b[1,3] + 100.0001 delta[1,3,44.0] >= 44.0001
 contribution_weight[280]: - w[3] + contribution[1,3,44.0] <= 0
 contribution_indicator[280]: - delta[1,3,44.0] + contribution[1,3,44.0]
   <= 0
 contribution_lower[280]: - w[3] - delta[1,3,44.0] + contribution[1,3,44.0]
   >= -1
 criterion_pass[281]: b[1,3] + 100.0001 delta[1,3,47.0] <= 147.0001
 criterion_fail[281]: b[1,3] + 100.0001 delta[1,3,47.0] >= 47.0001
 contribution_weight[281]: - w[3] + contribution[1,3,47.0] <= 0
 contribution_indicator[281]: - delta[1,3,47.0] + contribution[1,3,47.0]
   <= 0
 contribution_lower[281]: - w[3] - delta[1,3,47.0] + contribution[1,3,47.0]
   >= -1
 criterion_pass[282]: b[1,3] + 100.0001 delta[1,3,48.0] <= 148.0001
 criterion_fail[282]: b[1,3] + 100.0001 delta[1,3,48.0] >= 48.0001
 contribution_weight[282]: - w[3] + contribution[1,3,48.0] <= 0
 contribution_indicator[282]: - delta[1,3,48.0] + contribution[1,3,48.0]
   <= 0
 contribution_lower[282]: - w[3] - delta[1,3,48.0] + contribution[1,3,48.0]
   >= -1
 criterion_pass[283]: b[1,3] + 100.0001 delta[1,3,51.0] <= 151.0001
 criterion_fail[283]: b[1,3] + 100.0001 delta[1,3,51.0] >= 51.0001
 contribution_weight[283]: - w[3] + contribution[1,3,51.0] <= 0
 contribution_indicator[283]: - delta[1,3,51.0] + contribution[1,3,51.0]
   <= 0
 contribution_lower[283]: - w[3] - delta[1,3,51.0] + contribution[1,3,51.0]
   >= -1
 criterion_pass[284]: b[1,3] + 100.0001 delta[1,3,54.0] <= 154.0001
 criterion_fail[284]: b[1,3] + 100.0001 delta[1,3,54.0] >= 54.0001
 contribution_weight[284]: - w[3] + contribution[1,3,54.0] <= 0
 contribution_indicator[284]: - delta[1,3,54.0] + contribution[1,3,54.0]
   <= 0
 contribution_lower[284]: - w[3] - delta[1,3,54.0] + contribution[1,3,54.0]
   >= -1
 criterion_pass[285]: b[1,3] + 100.0001 delta[1,3,55.0] <= 155.0001
 criterion_fail[285]: b[1,3] + 100.0001 delta[1,3,55.0] >= 55.0001
 contribution_weight[285]: - w[3] + contribution[1,3,55.0] <= 0
 contribution_indicator[285]: - delta[1,3,55.0] + contribution[1,3,55.0]
   <= 0
 contribution_lower[285]: - w[3] - delta[1,3,55.0] + contribution[1,3,55.0]
   >= -1
 criterion_pass[286]: b[1,3] + 100.0001 delta[1,3,56.0] <= 156.0001
 criterion_fail[286]: b[1,3] + 100.0001 delta[1,3,56.0] >= 56.0001
 contribution_weight[286]: - w[3] + contribution[1,3,56.0] <= 0
 contribution_indicator[286]: - delta[1,3,56.0] + contribution[1,3,56.0]
   <= 0
 contribution_lower[286]: - w[3] - delta[1,3,56.0] + contribution[1,3,56.0]
   >= -1
 criterion_pass[287]: b[1,3] + 100.0001 delta[1,3,60.0] <= 160.0001
 criterion_fail[287]: b[1,3] + 100.0001 delta[1,3,60.0] >= 60.0001
 contribution_weight[287]: - w[3] + contribution[1,3,60.0] <= 0
 contribution_indicator[287]: - delta[1,3,60.0] + contribution[1,3,60.0]
   <= 0
 contribution_lower[287]: - w[3] - delta[1,3,60.0] + contribution[1,3,60.0]
   >= -1
 criterion_pass[288]: b[1,3] + 100.0001 delta[1,3,63.0] <= 163.0001
 criterion_fail[288]: b[1,3] + 100.0001 delta[1,3,63.0] >= 63.0001
 contribution_weight[288]: - w[3] + contribution[1,3,63.0] <= 0
 contribution_indicator[288]: - delta[1,3,63.0] + contribution[1,3,63.0]
   <= 0
 contribution_lower[288]: - w[3] - delta[1,3,63.0] + contribution[1,3,63.0]
   >= -1
 criterion_pass[289]: b[1,3] + 100.0001 delta[1,3,65.0] <= 165.0001
 criterion_fail[289]: b[1,3] + 100.0001 delta[1,3,65.0] >= 65.0001
 contribution_weight[289]: - w[3] + contribution[1,3,65.0] <= 0
 contribution_indicator[289]: - delta[1,3,65.0] + contribution[1,3,65.0]
   <= 0
 contribution_lower[289]: - w[3] - delta[1,3,65.0] + contribution[1,3,65.0]
   >= -1
 criterion_pass[290]: b[1,3] + 100.0001 delta[1,3,68.0] <= 168.0001
 criterion_fail[290]: b[1,3] + 100.0001 delta[1,3,68.0] >= 68.0001
 contribution_weight[290]: - w[3] + contribution[1,3,68.0] <= 0
 contribution_indicator[290]: - delta[1,3,68.0] + contribution[1,3,68.0]
   <= 0
 contribution_lower[290]: - w[3] - delta[1,3,68.0] + contribution[1,3,68.0]
   >= -1
 criterion_pass[291]: b[1,3] + 100.0001 delta[1,3,71.0] <= 171.0001
 criterion_fail[291]: b[1,3] + 100.0001 delta[1,3,71.0] >= 71.0001
 contribution_weight[291]: - w[3] + contribution[1,3,71.0] <= 0
 contribution_indicator[291]: - delta[1,3,71.0] + contribution[1,3,71.0]
   <= 0
 contribution_lower[291]: - w[3] - delta[1,3,71.0] + contribution[1,3,71.0]
   >= -1
 criterion_pass[292]: b[1,3] + 100.0001 delta[1,3,73.0] <= 173.0001
 criterion_fail[292]: b[1,3] + 100.0001 delta[1,3,73.0] >= 73.0001
 contribution_weight[292]: - w[3] + contribution[1,3,73.0] <= 0
 contribution_indicator[292]: - delta[1,3,73.0] + contribution[1,3,73.0]
   <= 0
 contribution_lower[292]: - w[3] - delta[1,3,73.0] + contribution[1,3,73.0]
   >= -1
 criterion_pass[293]: b[1,3] + 100.0001 delta[1,3,75.0] <= 175.0001
 criterion_fail[293]: b[1,3] + 100.0001 delta[1,3,75.0] >= 75.0001
 contribution_weight[293]: - w[3] + contribution[1,3,75.0] <= 0
 contribution_indicator[293]: - delta[1,3,75.0] + contribution[1,3,75.0]
   <= 0
 contribution_lower[293]: - w[3] - delta[1,3,75.0] + contribution[1,3,75.0]
   >= -1
 criterion_pass[294]: b[1,3] + 100.0001 delta[1,3,77.0] <= 177.0001
 criterion_fail[294]: b[1,3] + 100.0001 delta[1,3,77.0] >= 77.0001
 contribution_weight[294]: - w[3] + contribution[1,3,77.0] <= 0
 contribution_indicator[294]: - delta[1,3,77.0] + contribution[1,3,77.0]
   <= 0
 contribution_lower[294]: - w[3] - delta[1,3,77.0] + contribution[1,3,77.0]
   >= -1
 criterion_pass[295]: b[1,3] + 100.0001 delta[1,3,80.0] <= 180.0001
 criterion_fail[295]: b[1,3] + 100.0001 delta[1,3,80.0] >= 80.0001
 contribution_weight[295]: - w[3] + contribution[1,3,80.0] <= 0
 contribution_indicator[295]: - delta[1,3,80.0] + contribution[1,3,80.0]
   <= 0
 contribution_lower[295]: - w[3] - delta[1,3,80.0] + contribution[1,3,80.0]
   >= -1
 criterion_pass[296]: b[1,3] + 100.0001 delta[1,3,85.0] <= 185.0001
 criterion_fail[296]: b[1,3] + 100.0001 delta[1,3,85.0] >= 85.0001
 contribution_weight[296]: - w[3] + contribution[1,3,85.0] <= 0
 contribution_indicator[296]: - delta[1,3,85.0] + contribution[1,3,85.0]
   <= 0
 contribution_lower[296]: - w[3] - delta[1,3,85.0] + contribution[1,3,85.0]
   >= -1
 criterion_pass[297]: b[1,3] + 100.0001 delta[1,3,86.0] <= 186.0001
 criterion_fail[297]: b[1,3] + 100.0001 delta[1,3,86.0] >= 86.0001
 contribution_weight[297]: - w[3] + contribution[1,3,86.0] <= 0
 contribution_indicator[297]: - delta[1,3,86.0] + contribution[1,3,86.0]
   <= 0
 contribution_lower[297]: - w[3] - delta[1,3,86.0] + contribution[1,3,86.0]
   >= -1
 criterion_pass[298]: b[1,3] + 100.0001 delta[1,3,94.0] <= 194.0001
 criterion_fail[298]: b[1,3] + 100.0001 delta[1,3,94.0] >= 94.0001
 contribution_weight[298]: - w[3] + contribution[1,3,94.0] <= 0
 contribution_indicator[298]: - delta[1,3,94.0] + contribution[1,3,94.0]
   <= 0
 contribution_lower[298]: - w[3] - delta[1,3,94.0] + contribution[1,3,94.0]
   >= -1
 criterion_pass[299]: b[1,4] + 100.0001 delta[1,4,0.0] <= 100.0001
 criterion_fail[299]: b[1,4] + 100.0001 delta[1,4,0.0] >= 0.0001
 contribution_weight[299]: - w[4] + contribution[1,4,0.0] <= 0
 contribution_indicator[299]: - delta[1,4,0.0] + contribution[1,4,0.0]
   <= 0
 contribution_lower[299]: - w[4] - delta[1,4,0.0] + contribution[1,4,0.0]
   >= -1
 criterion_pass[300]: b[1,4] + 100.0001 delta[1,4,6.0] <= 106.0001
 criterion_fail[300]: b[1,4] + 100.0001 delta[1,4,6.0] >= 6.0001
 contribution_weight[300]: - w[4] + contribution[1,4,6.0] <= 0
 contribution_indicator[300]: - delta[1,4,6.0] + contribution[1,4,6.0]
   <= 0
 contribution_lower[300]: - w[4] - delta[1,4,6.0] + contribution[1,4,6.0]
   >= -1
 criterion_pass[301]: b[1,4] + 100.0001 delta[1,4,9.0] <= 109.0001
 criterion_fail[301]: b[1,4] + 100.0001 delta[1,4,9.0] >= 9.0001
 contribution_weight[301]: - w[4] + contribution[1,4,9.0] <= 0
 contribution_indicator[301]: - delta[1,4,9.0] + contribution[1,4,9.0]
   <= 0
 contribution_lower[301]: - w[4] - delta[1,4,9.0] + contribution[1,4,9.0]
   >= -1
 criterion_pass[302]: b[1,4] + 100.0001 delta[1,4,10.0] <= 110.0001
 criterion_fail[302]: b[1,4] + 100.0001 delta[1,4,10.0] >= 10.0001
 contribution_weight[302]: - w[4] + contribution[1,4,10.0] <= 0
 contribution_indicator[302]: - delta[1,4,10.0] + contribution[1,4,10.0]
   <= 0
 contribution_lower[302]: - w[4] - delta[1,4,10.0] + contribution[1,4,10.0]
   >= -1
 criterion_pass[303]: b[1,4] + 100.0001 delta[1,4,13.0] <= 113.0001
 criterion_fail[303]: b[1,4] + 100.0001 delta[1,4,13.0] >= 13.0001
 contribution_weight[303]: - w[4] + contribution[1,4,13.0] <= 0
 contribution_indicator[303]: - delta[1,4,13.0] + contribution[1,4,13.0]
   <= 0
 contribution_lower[303]: - w[4] - delta[1,4,13.0] + contribution[1,4,13.0]
   >= -1
 criterion_pass[304]: b[1,4] + 100.0001 delta[1,4,16.0] <= 116.0001
 criterion_fail[304]: b[1,4] + 100.0001 delta[1,4,16.0] >= 16.0001
 contribution_weight[304]: - w[4] + contribution[1,4,16.0] <= 0
 contribution_indicator[304]: - delta[1,4,16.0] + contribution[1,4,16.0]
   <= 0
 contribution_lower[304]: - w[4] - delta[1,4,16.0] + contribution[1,4,16.0]
   >= -1
 criterion_pass[305]: b[1,4] + 100.0001 delta[1,4,17.0] <= 117.0001
 criterion_fail[305]: b[1,4] + 100.0001 delta[1,4,17.0] >= 17.0001
 contribution_weight[305]: - w[4] + contribution[1,4,17.0] <= 0
 contribution_indicator[305]: - delta[1,4,17.0] + contribution[1,4,17.0]
   <= 0
 contribution_lower[305]: - w[4] - delta[1,4,17.0] + contribution[1,4,17.0]
   >= -1
 criterion_pass[306]: b[1,4] + 100.0001 delta[1,4,19.0] <= 119.0001
 criterion_fail[306]: b[1,4] + 100.0001 delta[1,4,19.0] >= 19.0001
 contribution_weight[306]: - w[4] + contribution[1,4,19.0] <= 0
 contribution_indicator[306]: - delta[1,4,19.0] + contribution[1,4,19.0]
   <= 0
 contribution_lower[306]: - w[4] - delta[1,4,19.0] + contribution[1,4,19.0]
   >= -1
 criterion_pass[307]: b[1,4] + 100.0001 delta[1,4,30.0] <= 130.0001
 criterion_fail[307]: b[1,4] + 100.0001 delta[1,4,30.0] >= 30.0001
 contribution_weight[307]: - w[4] + contribution[1,4,30.0] <= 0
 contribution_indicator[307]: - delta[1,4,30.0] + contribution[1,4,30.0]
   <= 0
 contribution_lower[307]: - w[4] - delta[1,4,30.0] + contribution[1,4,30.0]
   >= -1
 criterion_pass[308]: b[1,4] + 100.0001 delta[1,4,36.0] <= 136.0001
 criterion_fail[308]: b[1,4] + 100.0001 delta[1,4,36.0] >= 36.0001
 contribution_weight[308]: - w[4] + contribution[1,4,36.0] <= 0
 contribution_indicator[308]: - delta[1,4,36.0] + contribution[1,4,36.0]
   <= 0
 contribution_lower[308]: - w[4] - delta[1,4,36.0] + contribution[1,4,36.0]
   >= -1
 criterion_pass[309]: b[1,4] + 100.0001 delta[1,4,38.0] <= 138.0001
 criterion_fail[309]: b[1,4] + 100.0001 delta[1,4,38.0] >= 38.0001
 contribution_weight[309]: - w[4] + contribution[1,4,38.0] <= 0
 contribution_indicator[309]: - delta[1,4,38.0] + contribution[1,4,38.0]
   <= 0
 contribution_lower[309]: - w[4] - delta[1,4,38.0] + contribution[1,4,38.0]
   >= -1
 criterion_pass[310]: b[1,4] + 100.0001 delta[1,4,40.0] <= 140.0001
 criterion_fail[310]: b[1,4] + 100.0001 delta[1,4,40.0] >= 40.0001
 contribution_weight[310]: - w[4] + contribution[1,4,40.0] <= 0
 contribution_indicator[310]: - delta[1,4,40.0] + contribution[1,4,40.0]
   <= 0
 contribution_lower[310]: - w[4] - delta[1,4,40.0] + contribution[1,4,40.0]
   >= -1
 criterion_pass[311]: b[1,4] + 100.0001 delta[1,4,41.0] <= 141.0001
 criterion_fail[311]: b[1,4] + 100.0001 delta[1,4,41.0] >= 41.0001
 contribution_weight[311]: - w[4] + contribution[1,4,41.0] <= 0
 contribution_indicator[311]: - delta[1,4,41.0] + contribution[1,4,41.0]
   <= 0
 contribution_lower[311]: - w[4] - delta[1,4,41.0] + contribution[1,4,41.0]
   >= -1
 criterion_pass[312]: b[1,4] + 100.0001 delta[1,4,42.0] <= 142.0001
 criterion_fail[312]: b[1,4] + 100.0001 delta[1,4,42.0] >= 42.0001
 contribution_weight[312]: - w[4] + contribution[1,4,42.0] <= 0
 contribution_indicator[312]: - delta[1,4,42.0] + contribution[1,4,42.0]
   <= 0
 contribution_lower[312]: - w[4] - delta[1,4,42.0] + contribution[1,4,42.0]
   >= -1
 criterion_pass[313]: b[1,4] + 100.0001 delta[1,4,43.0] <= 143.0001
 criterion_fail[313]: b[1,4] + 100.0001 delta[1,4,43.0] >= 43.0001
 contribution_weight[313]: - w[4] + contribution[1,4,43.0] <= 0
 contribution_indicator[313]: - delta[1,4,43.0] + contribution[1,4,43.0]
   <= 0
 contribution_lower[313]: - w[4] - delta[1,4,43.0] + contribution[1,4,43.0]
   >= -1
 criterion_pass[314]: b[1,4] + 100.0001 delta[1,4,45.0] <= 145.0001
 criterion_fail[314]: b[1,4] + 100.0001 delta[1,4,45.0] >= 45.0001
 contribution_weight[314]: - w[4] + contribution[1,4,45.0] <= 0
 contribution_indicator[314]: - delta[1,4,45.0] + contribution[1,4,45.0]
   <= 0
 contribution_lower[314]: - w[4] - delta[1,4,45.0] + contribution[1,4,45.0]
   >= -1
 criterion_pass[315]: b[1,4] + 100.0001 delta[1,4,47.0] <= 147.0001
 criterion_fail[315]: b[1,4] + 100.0001 delta[1,4,47.0] >= 47.0001
 contribution_weight[315]: - w[4] + contribution[1,4,47.0] <= 0
 contribution_indicator[315]: - delta[1,4,47.0] + contribution[1,4,47.0]
   <= 0
 contribution_lower[315]: - w[4] - delta[1,4,47.0] + contribution[1,4,47.0]
   >= -1
 criterion_pass[316]: b[1,4] + 100.0001 delta[1,4,48.0] <= 148.0001
 criterion_fail[316]: b[1,4] + 100.0001 delta[1,4,48.0] >= 48.0001
 contribution_weight[316]: - w[4] + contribution[1,4,48.0] <= 0
 contribution_indicator[316]: - delta[1,4,48.0] + contribution[1,4,48.0]
   <= 0
 contribution_lower[316]: - w[4] - delta[1,4,48.0] + contribution[1,4,48.0]
   >= -1
 criterion_pass[317]: b[1,4] + 100.0001 delta[1,4,50.0] <= 150.0001
 criterion_fail[317]: b[1,4] + 100.0001 delta[1,4,50.0] >= 50.0001
 contribution_weight[317]: - w[4] + contribution[1,4,50.0] <= 0
 contribution_indicator[317]: - delta[1,4,50.0] + contribution[1,4,50.0]
   <= 0
 contribution_lower[317]: - w[4] - delta[1,4,50.0] + contribution[1,4,50.0]
   >= -1
 criterion_pass[318]: b[1,4] + 100.0001 delta[1,4,52.0] <= 152.0001
 criterion_fail[318]: b[1,4] + 100.0001 delta[1,4,52.0] >= 52.0001
 contribution_weight[318]: - w[4] + contribution[1,4,52.0] <= 0
 contribution_indicator[318]: - delta[1,4,52.0] + contribution[1,4,52.0]
   <= 0
 contribution_lower[318]: - w[4] - delta[1,4,52.0] + contribution[1,4,52.0]
   >= -1
 criterion_pass[319]: b[1,4] + 100.0001 delta[1,4,59.0] <= 159.0001
 criterion_fail[319]: b[1,4] + 100.0001 delta[1,4,59.0] >= 59.0001
 contribution_weight[319]: - w[4] + contribution[1,4,59.0] <= 0
 contribution_indicator[319]: - delta[1,4,59.0] + contribution[1,4,59.0]
   <= 0
 contribution_lower[319]: - w[4] - delta[1,4,59.0] + contribution[1,4,59.0]
   >= -1
 criterion_pass[320]: b[1,4] + 100.0001 delta[1,4,60.0] <= 160.0001
 criterion_fail[320]: b[1,4] + 100.0001 delta[1,4,60.0] >= 60.0001
 contribution_weight[320]: - w[4] + contribution[1,4,60.0] <= 0
 contribution_indicator[320]: - delta[1,4,60.0] + contribution[1,4,60.0]
   <= 0
 contribution_lower[320]: - w[4] - delta[1,4,60.0] + contribution[1,4,60.0]
   >= -1
 criterion_pass[321]: b[1,4] + 100.0001 delta[1,4,62.0] <= 162.0001
 criterion_fail[321]: b[1,4] + 100.0001 delta[1,4,62.0] >= 62.0001
 contribution_weight[321]: - w[4] + contribution[1,4,62.0] <= 0
 contribution_indicator[321]: - delta[1,4,62.0] + contribution[1,4,62.0]
   <= 0
 contribution_lower[321]: - w[4] - delta[1,4,62.0] + contribution[1,4,62.0]
   >= -1
 criterion_pass[322]: b[1,4] + 100.0001 delta[1,4,63.0] <= 163.0001
 criterion_fail[322]: b[1,4] + 100.0001 delta[1,4,63.0] >= 63.0001
 contribution_weight[322]: - w[4] + contribution[1,4,63.0] <= 0
 contribution_indicator[322]: - delta[1,4,63.0] + contribution[1,4,63.0]
   <= 0
 contribution_lower[322]: - w[4] - delta[1,4,63.0] + contribution[1,4,63.0]
   >= -1
 criterion_pass[323]: b[1,4] + 100.0001 delta[1,4,64.0] <= 164.0001
 criterion_fail[323]: b[1,4] + 100.0001 delta[1,4,64.0] >= 64.0001
 contribution_weight[323]: - w[4] + contribution[1,4,64.0] <= 0
 contribution_indicator[323]: - delta[1,4,64.0] + contribution[1,4,64.0]
   <= 0
 contribution_lower[323]: - w[4] - delta[1,4,64.0] + contribution[1,4,64.0]
   >= -1
 criterion_pass[324]: b[1,4] + 100.0001 delta[1,4,65.0] <= 165.0001
 criterion_fail[324]: b[1,4] + 100.0001 delta[1,4,65.0] >= 65.0001
 contribution_weight[324]: - w[4] + contribution[1,4,65.0] <= 0
 contribution_indicator[324]: - delta[1,4,65.0] + contribution[1,4,65.0]
   <= 0
 contribution_lower[324]: - w[4] - delta[1,4,65.0] + contribution[1,4,65.0]
   >= -1
 criterion_pass[325]: b[1,4] + 100.0001 delta[1,4,67.0] <= 167.0001
 criterion_fail[325]: b[1,4] + 100.0001 delta[1,4,67.0] >= 67.0001
 contribution_weight[325]: - w[4] + contribution[1,4,67.0] <= 0
 contribution_indicator[325]: - delta[1,4,67.0] + contribution[1,4,67.0]
   <= 0
 contribution_lower[325]: - w[4] - delta[1,4,67.0] + contribution[1,4,67.0]
   >= -1
 criterion_pass[326]: b[1,4] + 100.0001 delta[1,4,70.0] <= 170.0001
 criterion_fail[326]: b[1,4] + 100.0001 delta[1,4,70.0] >= 70.0001
 contribution_weight[326]: - w[4] + contribution[1,4,70.0] <= 0
 contribution_indicator[326]: - delta[1,4,70.0] + contribution[1,4,70.0]
   <= 0
 contribution_lower[326]: - w[4] - delta[1,4,70.0] + contribution[1,4,70.0]
   >= -1
 criterion_pass[327]: b[1,4] + 100.0001 delta[1,4,75.0] <= 175.0001
 criterion_fail[327]: b[1,4] + 100.0001 delta[1,4,75.0] >= 75.0001
 contribution_weight[327]: - w[4] + contribution[1,4,75.0] <= 0
 contribution_indicator[327]: - delta[1,4,75.0] + contribution[1,4,75.0]
   <= 0
 contribution_lower[327]: - w[4] - delta[1,4,75.0] + contribution[1,4,75.0]
   >= -1
 criterion_pass[328]: b[1,4] + 100.0001 delta[1,4,78.0] <= 178.0001
 criterion_fail[328]: b[1,4] + 100.0001 delta[1,4,78.0] >= 78.0001
 contribution_weight[328]: - w[4] + contribution[1,4,78.0] <= 0
 contribution_indicator[328]: - delta[1,4,78.0] + contribution[1,4,78.0]
   <= 0
 contribution_lower[328]: - w[4] - delta[1,4,78.0] + contribution[1,4,78.0]
   >= -1
 criterion_pass[329]: b[1,4] + 100.0001 delta[1,4,81.0] <= 181.0001
 criterion_fail[329]: b[1,4] + 100.0001 delta[1,4,81.0] >= 81.0001
 contribution_weight[329]: - w[4] + contribution[1,4,81.0] <= 0
 contribution_indicator[329]: - delta[1,4,81.0] + contribution[1,4,81.0]
   <= 0
 contribution_lower[329]: - w[4] - delta[1,4,81.0] + contribution[1,4,81.0]
   >= -1
 criterion_pass[330]: b[1,4] + 100.0001 delta[1,4,82.0] <= 182.0001
 criterion_fail[330]: b[1,4] + 100.0001 delta[1,4,82.0] >= 82.0001
 contribution_weight[330]: - w[4] + contribution[1,4,82.0] <= 0
 contribution_indicator[330]: - delta[1,4,82.0] + contribution[1,4,82.0]
   <= 0
 contribution_lower[330]: - w[4] - delta[1,4,82.0] + contribution[1,4,82.0]
   >= -1
 criterion_pass[331]: b[1,4] + 100.0001 delta[1,4,83.0] <= 183.0001
 criterion_fail[331]: b[1,4] + 100.0001 delta[1,4,83.0] >= 83.0001
 contribution_weight[331]: - w[4] + contribution[1,4,83.0] <= 0
 contribution_indicator[331]: - delta[1,4,83.0] + contribution[1,4,83.0]
   <= 0
 contribution_lower[331]: - w[4] - delta[1,4,83.0] + contribution[1,4,83.0]
   >= -1
 criterion_pass[332]: b[1,4] + 100.0001 delta[1,4,88.0] <= 188.0001
 criterion_fail[332]: b[1,4] + 100.0001 delta[1,4,88.0] >= 88.0001
 contribution_weight[332]: - w[4] + contribution[1,4,88.0] <= 0
 contribution_indicator[332]: - delta[1,4,88.0] + contribution[1,4,88.0]
   <= 0
 contribution_lower[332]: - w[4] - delta[1,4,88.0] + contribution[1,4,88.0]
   >= -1
 lower_class[0]: - lambda + contribution[0,0,5.0] + contribution[0,1,61.0]
   + contribution[0,2,9.0] + contribution[0,3,75.0]
   + contribution[0,4,42.0] + 1.0001 error[0] >= 0
 upper_class[0]: - lambda + contribution[1,0,5.0] + contribution[1,1,61.0]
   + contribution[1,2,9.0] + contribution[1,3,75.0]
   + contribution[1,4,42.0] - 1.0001 error[0] <= -0.0001
 lower_class[1]: - lambda + contribution[1,0,64.0] + contribution[1,1,92.0]
   + contribution[1,2,93.0] + contribution[1,3,80.0]
   + contribution[1,4,30.0] + 1.0001 error[1] >= 0
 lower_class[2]: - lambda + contribution[1,0,54.0] + contribution[1,1,96.0]
   + contribution[1,2,28.0] + contribution[1,3,54.0]
   + contribution[1,4,81.0] + 1.0001 error[2] >= 0
 lower_class[3]: - lambda + contribution[1,0,68.0] + contribution[1,1,53.0]
   + contribution[1,2,37.0] + contribution[1,3,35.0]
   + contribution[1,4,50.0] + 1.0001 error[3] >= 0
 upper_class[4]: - lambda + contribution[0,0,90.0] + contribution[0,1,5.0]
   + contribution[0,2,7.0] + contribution[0,3,38.0]
   + contribution[0,4,94.0] - 1.0001 error[4] <= -0.0001
 lower_class[5]: - lambda + contribution[1,0,1.0] + contribution[1,1,53.0]
   + contribution[1,2,90.0] + contribution[1,3,73.0]
   + contribution[1,4,50.0] + 1.0001 error[5] >= 0
 upper_class[6]: - lambda + contribution[0,0,32.0] + contribution[0,1,48.0]
   + contribution[0,2,38.0] + contribution[0,3,23.0]
   + contribution[0,4,17.0] - 1.0001 error[6] <= -0.0001
 lower_class[7]: - lambda + contribution[0,0,60.0] + contribution[0,1,84.0]
   + contribution[0,2,77.0] + contribution[0,3,26.0]
   + contribution[0,4,42.0] + 1.0001 error[7] >= 0
 upper_class[7]: - lambda + contribution[1,0,60.0] + contribution[1,1,84.0]
   + contribution[1,2,77.0] + contribution[1,3,26.0]
   + contribution[1,4,42.0] - 1.0001 error[7] <= -0.0001
 lower_class[8]: - lambda + contribution[0,0,10.0] + contribution[0,1,38.0]
   + contribution[0,2,27.0] + contribution[0,3,85.0]
   + contribution[0,4,88.0] + 1.0001 error[8] >= 0
 upper_class[8]: - lambda + contribution[1,0,10.0] + contribution[1,1,38.0]
   + contribution[1,2,27.0] + contribution[1,3,85.0]
   + contribution[1,4,88.0] - 1.0001 error[8] <= -0.0001
 upper_class[9]: - lambda + contribution[0,0,60.0] + contribution[0,1,32.0]
   + contribution[0,2,80.0] + contribution[0,3,0.0]
   + contribution[0,4,56.0] - 1.0001 error[9] <= -0.0001
 lower_class[10]: - lambda + contribution[1,0,70.0]
   + contribution[1,1,86.0] + contribution[1,2,57.0]
   + contribution[1,3,65.0] + contribution[1,4,10.0] + 1.0001 error[10]
   >= 0
 lower_class[11]: - lambda + contribution[0,0,83.0]
   + contribution[0,1,36.0] + contribution[0,2,76.0]
   + contribution[0,3,47.0] + contribution[0,4,6.0] + 1.0001 error[11]
   >= 0
 upper_class[11]: - lambda + contribution[1,0,83.0]
   + contribution[1,1,36.0] + contribution[1,2,76.0]
   + contribution[1,3,47.0] + contribution[1,4,6.0] - 1.0001 error[11]
   <= -0.0001
 lower_class[12]: - lambda + contribution[1,0,58.0]
   + contribution[1,1,81.0] + contribution[1,2,86.0]
   + contribution[1,3,71.0] + contribution[1,4,65.0] + 1.0001 error[12]
   >= 0
 lower_class[13]: - lambda + contribution[0,0,37.0]
   + contribution[0,1,46.0] + contribution[0,2,100.0]
   + contribution[0,3,85.0] + contribution[0,4,59.0] + 1.0001 error[13]
   >= 0
 upper_class[13]: - lambda + contribution[1,0,37.0]
   + contribution[1,1,46.0] + contribution[1,2,100.0]
   + contribution[1,3,85.0] + contribution[1,4,59.0] - 1.0001 error[13]
   <= -0.0001
 lower_class[14]: - lambda + contribution[1,0,36.0]
   + contribution[1,1,63.0] + contribution[1,2,14.0]
   + contribution[1,3,63.0] + contribution[1,4,59.0] + 1.0001 error[14]
   >= 0
 lower_class[15]: - lambda + contribution[1,0,99.0]
   + contribution[1,1,55.0] + contribution[1,2,61.0]
   + contribution[1,3,13.0] + contribution[1,4,70.0] + 1.0001 error[15]
   >= 0
 lower_class[16]: - lambda + contribution[0,0,91.0] + contribution[0,1,6.0]
   + contribution[0,2,93.0] + contribution[0,3,41.0]
   + contribution[0,4,48.0] + 1.0001 error[16] >= 0
 upper_class[16]: - lambda + contribution[1,0,91.0] + contribution[1,1,6.0]
   + contribution[1,2,93.0] + contribution[1,3,41.0]
   + contribution[1,4,48.0] - 1.0001 error[16] <= -0.0001
 upper_class[17]: - lambda + contribution[0,0,47.0] + contribution[0,1,5.0]
   + contribution[0,2,38.0] + contribution[0,3,0.0]
   + contribution[0,4,45.0] - 1.0001 error[17] <= -0.0001
 upper_class[18]: - lambda + contribution[0,0,69.0]
   + contribution[0,1,32.0] + contribution[0,2,72.0]
   + contribution[0,3,33.0] + contribution[0,4,99.0] - 1.0001 error[18]
   <= -0.0001
 lower_class[19]: - lambda + contribution[1,0,93.0]
   + contribution[1,1,76.0] + contribution[1,2,100.0]
   + contribution[1,3,19.0] + contribution[1,4,63.0] + 1.0001 error[19]
   >= 0
 lower_class[20]: - lambda + contribution[0,0,85.0]
   + contribution[0,1,41.0] + contribution[0,2,12.0]
   + contribution[0,3,94.0] + contribution[0,4,47.0] + 1.0001 error[20]
   >= 0
 upper_class[20]: - lambda + contribution[1,0,85.0]
   + contribution[1,1,41.0] + contribution[1,2,12.0]
   + contribution[1,3,94.0] + contribution[1,4,47.0] - 1.0001 error[20]
   <= -0.0001
 lower_class[21]: - lambda + contribution[0,0,99.0]
   + contribution[0,1,87.0] + contribution[0,2,100.0]
   + contribution[0,3,43.0] + contribution[0,4,16.0] + 1.0001 error[21]
   >= 0
 upper_class[21]: - lambda + contribution[1,0,99.0]
   + contribution[1,1,87.0] + contribution[1,2,100.0]
   + contribution[1,3,43.0] + contribution[1,4,16.0] - 1.0001 error[21]
   <= -0.0001
 lower_class[22]: - lambda + contribution[1,0,95.0]
   + contribution[1,1,57.0] + contribution[1,2,98.0]
   + contribution[1,3,60.0] + contribution[1,4,64.0] + 1.0001 error[22]
   >= 0
 upper_class[23]: - lambda + contribution[0,0,93.0]
   + contribution[0,1,34.0] + contribution[0,2,99.0]
   + contribution[0,3,31.0] + contribution[0,4,64.0] - 1.0001 error[23]
   <= -0.0001
 upper_class[24]: - lambda + contribution[0,0,22.0]
   + contribution[0,1,33.0] + contribution[0,2,78.0]
   + contribution[0,3,31.0] + contribution[0,4,30.0] - 1.0001 error[24]
   <= -0.0001
 lower_class[25]: - lambda + contribution[0,0,22.0]
   + contribution[0,1,72.0] + contribution[0,2,13.0]
   + contribution[0,3,38.0] + contribution[0,4,67.0] + 1.0001 error[25]
   >= 0
 upper_class[25]: - lambda + contribution[1,0,22.0]
   + contribution[1,1,72.0] + contribution[1,2,13.0]
   + contribution[1,3,38.0] + contribution[1,4,67.0] - 1.0001 error[25]
   <= -0.0001
 lower_class[26]: - lambda + contribution[0,0,30.0]
   + contribution[0,1,95.0] + contribution[0,2,29.0]
   + contribution[0,3,75.0] + contribution[0,4,41.0] + 1.0001 error[26]
   >= 0
 upper_class[26]: - lambda + contribution[1,0,30.0]
   + contribution[1,1,95.0] + contribution[1,2,29.0]
   + contribution[1,3,75.0] + contribution[1,4,41.0] - 1.0001 error[26]
   <= -0.0001
 upper_class[27]: - lambda + contribution[0,0,20.0]
   + contribution[0,1,12.0] + contribution[0,2,99.0]
   + contribution[0,3,54.0] + contribution[0,4,62.0] - 1.0001 error[27]
   <= -0.0001
 lower_class[28]: - lambda + contribution[0,0,59.0]
   + contribution[0,1,53.0] + contribution[0,2,77.0]
   + contribution[0,3,36.0] + contribution[0,4,17.0] + 1.0001 error[28]
   >= 0
 upper_class[28]: - lambda + contribution[1,0,59.0]
   + contribution[1,1,53.0] + contribution[1,2,77.0]
   + contribution[1,3,36.0] + contribution[1,4,17.0] - 1.0001 error[28]
   <= -0.0001
 upper_class[29]: - lambda + contribution[0,0,20.0]
   + contribution[0,1,23.0] + contribution[0,2,74.0]
   + contribution[0,3,65.0] + contribution[0,4,42.0] - 1.0001 error[29]
   <= -0.0001
 upper_class[30]: - lambda + contribution[0,0,62.0] + contribution[0,1,2.0]
   + contribution[0,2,4.0] + contribution[0,3,53.0]
   + contribution[0,4,76.0] - 1.0001 error[30] <= -0.0001
 upper_class[31]: - lambda + contribution[0,0,25.0]
   + contribution[0,1,33.0] + contribution[0,2,55.0]
   + contribution[0,3,76.0] + contribution[0,4,22.0] - 1.0001 error[31]
   <= -0.0001
 lower_class[32]: - lambda + contribution[1,0,92.0]
   + contribution[1,1,94.0] + contribution[1,2,56.0]
   + contribution[1,3,6.0] + contribution[1,4,83.0] + 1.0001 error[32]
   >= 0
 lower_class[33]: - lambda + contribution[0,0,37.0]
   + contribution[0,1,100.0] + contribution[0,2,60.0]
   + contribution[0,3,37.0] + contribution[0,4,38.0] + 1.0001 error[33]
   >= 0
 upper_class[33]: - lambda + contribution[1,0,37.0]
   + contribution[1,1,100.0] + contribution[1,2,60.0]
   + contribution[1,3,37.0] + contribution[1,4,38.0] - 1.0001 error[33]
   <= -0.0001
 upper_class[34]: - lambda + contribution[0,0,59.0] + contribution[0,1,9.0]
   + contribution[0,2,21.0] + contribution[0,3,57.0]
   + contribution[0,4,54.0] - 1.0001 error[34] <= -0.0001
 lower_class[35]: - lambda + contribution[1,0,96.0]
   + contribution[1,1,56.0] + contribution[1,2,26.0]
   + contribution[1,3,77.0] + contribution[1,4,75.0] + 1.0001 error[35]
   >= 0
 lower_class[36]: - lambda + contribution[0,0,66.0]
   + contribution[0,1,52.0] + contribution[0,2,100.0]
   + contribution[0,3,38.0] + contribution[0,4,0.0] + 1.0001 error[36]
   >= 0
 upper_class[36]: - lambda + contribution[1,0,66.0]
   + contribution[1,1,52.0] + contribution[1,2,100.0]
   + contribution[1,3,38.0] + contribution[1,4,0.0] - 1.0001 error[36]
   <= -0.0001
 lower_class[37]: - lambda + contribution[0,0,73.0]
   + contribution[0,1,17.0] + contribution[0,2,66.0]
   + contribution[0,3,48.0] + contribution[0,4,36.0] + 1.0001 error[37]
   >= 0
 upper_class[37]: - lambda + contribution[1,0,73.0]
   + contribution[1,1,17.0] + contribution[1,2,66.0]
   + contribution[1,3,48.0] + contribution[1,4,36.0] - 1.0001 error[37]
   <= -0.0001
 upper_class[38]: - lambda + contribution[0,0,26.0]
   + contribution[0,1,27.0] + contribution[0,2,69.0]
   + contribution[0,3,85.0] + contribution[0,4,16.0] - 1.0001 error[38]
   <= -0.0001
 lower_class[39]: - lambda + contribution[1,0,16.0]
   + contribution[1,1,91.0] + contribution[1,2,87.0]
   + contribution[1,3,55.0] + contribution[1,4,78.0] + 1.0001 error[39]
   >= 0
 upper_class[40]: - lambda + contribution[0,0,46.0]
   + contribution[0,1,29.0] + contribution[0,2,23.0]
   + contribution[0,3,88.0] + contribution[0,4,6.0] - 1.0001 error[40]
   <= -0.0001
 lower_class[41]: - lambda + contribution[1,0,41.0]
   + contribution[1,1,54.0] + contribution[1,2,91.0]
   + contribution[1,3,36.0] + contribution[1,4,82.0] + 1.0001 error[41]
   >= 0
 lower_class[42]: - lambda + contribution[0,0,38.0] + contribution[0,1,8.0]
   + contribution[0,2,99.0] + contribution[0,3,35.0]
   + contribution[0,4,52.0] + 1.0001 error[42] >= 0
 upper_class[42]: - lambda + contribution[1,0,38.0] + contribution[1,1,8.0]
   + contribution[1,2,99.0] + contribution[1,3,35.0]
   + contribution[1,4,52.0] - 1.0001 error[42] <= -0.0001
 lower_class[43]: - lambda + contribution[0,0,38.0]
   + contribution[0,1,38.0] + contribution[0,2,84.0]
   + contribution[0,3,39.0] + contribution[0,4,19.0] + 1.0001 error[43]
   >= 0
 upper_class[43]: - lambda + contribution[1,0,38.0]
   + contribution[1,1,38.0] + contribution[1,2,84.0]
   + contribution[1,3,39.0] + contribution[1,4,19.0] - 1.0001 error[43]
   <= -0.0001
 upper_class[44]: - lambda + contribution[0,0,81.0]
   + contribution[0,1,16.0] + contribution[0,2,43.0]
   + contribution[0,3,19.0] + contribution[0,4,64.0] - 1.0001 error[44]
   <= -0.0001
 lower_class[45]: - lambda + contribution[0,0,49.0]
   + contribution[0,1,48.0] + contribution[0,2,88.0]
   + contribution[0,3,56.0] + contribution[0,4,13.0] + 1.0001 error[45]
   >= 0
 upper_class[45]: - lambda + contribution[1,0,49.0]
   + contribution[1,1,48.0] + contribution[1,2,88.0]
   + contribution[1,3,56.0] + contribution[1,4,13.0] - 1.0001 error[45]
   <= -0.0001
 lower_class[46]: - lambda + contribution[0,0,86.0]
   + contribution[0,1,41.0] + contribution[0,2,37.0]
   + contribution[0,3,51.0] + contribution[0,4,9.0] + 1.0001 error[46]
   >= 0
 upper_class[46]: - lambda + contribution[1,0,86.0]
   + contribution[1,1,41.0] + contribution[1,2,37.0]
   + contribution[1,3,51.0] + contribution[1,4,9.0] - 1.0001 error[46]
   <= -0.0001
 upper_class[47]: - lambda + contribution[0,0,3.0] + contribution[0,1,54.0]
   + contribution[0,2,29.0] + contribution[0,3,23.0]
   + contribution[0,4,68.0] - 1.0001 error[47] <= -0.0001
 lower_class[48]: - lambda + contribution[0,0,11.0]
   + contribution[0,1,68.0] + contribution[0,2,3.0]
   + contribution[0,3,38.0] + contribution[0,4,42.0] + 1.0001 error[48]
   >= 0
 upper_class[48]: - lambda + contribution[1,0,11.0]
   + contribution[1,1,68.0] + contribution[1,2,3.0]
   + contribution[1,3,38.0] + contribution[1,4,42.0] - 1.0001 error[48]
   <= -0.0001
 lower_class[49]: - lambda + contribution[0,0,47.0]
   + contribution[0,1,38.0] + contribution[0,2,4.0]
   + contribution[0,3,44.0] + contribution[0,4,43.0] + 1.0001 error[49]
   >= 0
 upper_class[49]: - lambda + contribution[1,0,47.0]
   + contribution[1,1,38.0] + contribution[1,2,4.0]
   + contribution[1,3,44.0] + contribution[1,4,43.0] - 1.0001 error[49]
   <= -0.0001
 lower_class[50]: - lambda + contribution[0,0,56.0]
   + contribution[0,1,56.0] + contribution[0,2,69.0]
   + contribution[0,3,2.0] + contribution[0,4,38.0] + 1.0001 error[50]
   >= 0
 upper_class[50]: - lambda + contribution[1,0,56.0]
   + contribution[1,1,56.0] + contribution[1,2,69.0]
   + contribution[1,3,2.0] + contribution[1,4,38.0] - 1.0001 error[50]
   <= -0.0001
 upper_class[51]: - lambda + contribution[0,0,42.0]
   + contribution[0,1,73.0] + contribution[0,2,40.0]
   + contribution[0,3,13.0] + contribution[0,4,2.0] - 1.0001 error[51]
   <= -0.0001
 lower_class[52]: - lambda + contribution[0,0,3.0] + contribution[0,1,82.0]
   + contribution[0,2,7.0] + contribution[0,3,35.0]
   + contribution[0,4,52.0] + 1.0001 error[52] >= 0
 upper_class[52]: - lambda + contribution[1,0,3.0] + contribution[1,1,82.0]
   + contribution[1,2,7.0] + contribution[1,3,35.0]
   + contribution[1,4,52.0] - 1.0001 error[52] <= -0.0001
 lower_class[53]: - lambda + contribution[0,0,83.0] + contribution[0,1,6.0]
   + contribution[0,2,97.0] + contribution[0,3,47.0]
   + contribution[0,4,45.0] + 1.0001 error[53] >= 0
 upper_class[53]: - lambda + contribution[1,0,83.0] + contribution[1,1,6.0]
   + contribution[1,2,97.0] + contribution[1,3,47.0]
   + contribution[1,4,45.0] - 1.0001 error[53] <= -0.0001
 lower_class[54]: - lambda + contribution[0,0,40.0] + contribution[0,1,5.0]
   + contribution[0,2,77.0] + contribution[0,3,86.0]
   + contribution[0,4,62.0] + 1.0001 error[54] >= 0
 upper_class[54]: - lambda + contribution[1,0,40.0] + contribution[1,1,5.0]
   + contribution[1,2,77.0] + contribution[1,3,86.0]
   + contribution[1,4,62.0] - 1.0001 error[54] <= -0.0001
 lower_class[55]: - lambda + contribution[1,0,85.0]
   + contribution[1,1,80.0] + contribution[1,2,50.0]
   + contribution[1,3,34.0] + contribution[1,4,83.0] + 1.0001 error[55]
   >= 0
 lower_class[56]: - lambda + contribution[1,0,71.0]
   + contribution[1,1,65.0] + contribution[1,2,66.0]
   + contribution[1,3,68.0] + contribution[1,4,60.0] + 1.0001 error[56]
   >= 0
 lower_class[57]: - lambda + contribution[0,0,19.0]
   + contribution[0,1,48.0] + contribution[0,2,73.0]
   + contribution[0,3,23.0] + contribution[0,4,40.0] + 1.0001 error[57]
   >= 0
 upper_class[57]: - lambda + contribution[1,0,19.0]
   + contribution[1,1,48.0] + contribution[1,2,73.0]
   + contribution[1,3,23.0] + contribution[1,4,40.0] - 1.0001 error[57]
   <= -0.0001
 upper_class[58]: - lambda + contribution[0,0,33.0]
   + contribution[0,1,94.0] + contribution[0,2,77.0]
   + contribution[0,3,62.0] + contribution[0,4,22.0] - 1.0001 error[58]
   <= -0.0001
 upper_class[59]: - lambda + contribution[0,0,45.0]
   + contribution[0,1,50.0] + contribution[0,2,12.0]
   + contribution[0,3,18.0] + contribution[0,4,24.0] - 1.0001 error[59]
   <= -0.0001
Bounds
 w[0] <= 1
 w[1] <= 1
 w[2] <= 1
 w[3] <= 1
 w[4] <= 1
 b[0,0] <= 100
 b[0,1] <= 100
 b[0,2] <= 100
 b[0,3] <= 100
 b[0,4] <= 100
 b[1,0] <= 100
 b[1,1] <= 100
 b[1,2] <= 100
 b[1,3] <= 100
 b[1,4] <= 100
 lambda <= 1
 contribution[0,0,3.0] <= 1
 contribution[0,0,5.0] <= 1
 contribution[0,0,10.0] <= 1
 contribution[0,0,11.0] <= 1
 contribution[0,0,19.0] <= 1
 contribution[0,0,20.0] <= 1
 contribution[0,0,22.0] <= 1
 contribution[0,0,25.0] <= 1
 contribution[0,0,26.0] <= 1
 contribution[0,0,30.0] <= 1
 contribution[0,0,32.0] <= 1
 contribution[0,0,33.0] <= 1
 contribution[0,0,37.0] <= 1
 contribution[0,0,38.0] <= 1
 contribution[0,0,40.0] <= 1
 contribution[0,0,42.0] <= 1
 contribution[0,0,45.0] <= 1
 contribution[0,0,46.0] <= 1
 contribution[0,0,47.0] <= 1
 contribution[0,0,49.0] <= 1
 contribution[0,0,56.0] <= 1
 contribution[0,0,59.0] <= 1
 contribution[0,0,60.0] <= 1
 contribution[0,0,62.0] <= 1
 contribution[0,0,66.0] <= 1
 contribution[0,0,69.0] <= 1
 contribution[0,0,73.0] <= 1
 contribution[0,0,81.0] <= 1
 contribution[0,0,83.0] <= 1
 contribution[0,0,85.0] <= 1
 contribution[0,0,86.0] <= 1
 contribution[0,0,90.0] <= 1
 contribution[0,0,91.0] <= 1
 contribution[0,0,93.0] <= 1
 contribution[0,0,99.0] <= 1
 contribution[0,1,2.0] <= 1
 contribution[0,1,5.0] <= 1
 contribution[0,1,6.0] <= 1
 contribution[0,1,8.0] <= 1
 contribution[0,1,9.0] <= 1
 contribution[0,1,12.0] <= 1
 contribution[0,1,16.0] <= 1
 contribution[0,1,17.0] <= 1
 contribution[0,1,23.0] <= 1
 contribution[0,1,27.0] <= 1
 contribution[0,1,29.0] <= 1
 contribution[0,1,32.0] <= 1
 contribution[0,1,33.0] <= 1
 contribution[0,1,34.0] <= 1
 contribution[0,1,36.0] <= 1
 contribution[0,1,38.0] <= 1
 contribution[0,1,41.0] <= 1
 contribution[0,1,46.0] <= 1
 contribution[0,1,48.0] <= 1
 contribution[0,1,50.0] <= 1
 contribution[0,1,52.0] <= 1
 contribution[0,1,53.0] <= 1
 contribution[0,1,54.0] <= 1
 contribution[0,1,56.0] <= 1
 contribution[0,1,61.0] <= 1
 contribution[0,1,68.0] <= 1
 contribution[0,1,72.0] <= 1
 contribution[0,1,73.0] <= 1
 contribution[0,1,82.0] <= 1
 contribution[0,1,84.0] <= 1
 contribution[0,1,87.0] <= 1
 contribution[0,1,94.0] <= 1
 contribution[0,1,95.0] <= 1
 contribution[0,1,100.0] <= 1
 contribution[0,2,3.0] <= 1
 contribution[0,2,4.0] <= 1
 contribution[0,2,7.0] <= 1
 contribution[0,2,9.0] <= 1
 contribution[0,2,12.0] <= 1
 contribution[0,2,13.0] <= 1
 contribution[0,2,21.0] <= 1
 contribution[0,2,23.0] <= 1
 contribution[0,2,27.0] <= 1
 contribution[0,2,29.0] <= 1
 contribution[0,2,37.0] <= 1
 contribution[0,2,38.0] <= 1
 contribution[0,2,40.0] <= 1
 contribution[0,2,43.0] <= 1
 contribution[0,2,55.0] <= 1
 contribution[0,2,60.0] <= 1
 contribution[0,2,66.0] <= 1
 contribution[0,2,69.0] <= 1
 contribution[0,2,72.0] <= 1
 contribution[0,2,73.0] <= 1
 contribution[0,2,74.0] <= 1
 contribution[0,2,76.0] <= 1
 contribution[0,2,77.0] <= 1
 contribution[0,2,78.0] <= 1
 contribution[0,2,80.0] <= 1
 contribution[0,2,84.0] <= 1
 contribution[0,2,88.0] <= 1
 contribution[0,2,93.0] <= 1
 contribution[0,2,97.0] <= 1
 contribution[0,2,99.0] <= 1
 contribution[0,2,100.0] <= 1
 contribution[0,3,0.0] <= 1
 contribution[0,3,2.0] <= 1
 contribution[0,3,13.0] <= 1
 contribution[0,3,18.0] <= 1
 contribution[0,3,19.0] <= 1
 contribution[0,3,23.0] <= 1
 contribution[0,3,26.0] <= 1
 contribution[0,3,31.0] <= 1
 contribution[0,3,33.0] <= 1
 contribution[0,3,35.0] <= 1
 contribution[0,3,36.0] <= 1
 contribution[0,3,37.0] <= 1
 contribution[0,3,38.0] <= 1
 contribution[0,3,39.0] <= 1
 contribution[0,3,41.0] <= 1
 contribution[0,3,43.0] <= 1
 contribution[0,3,44.0] <= 1
 contribution[0,3,47.0] <= 1
 contribution[0,3,48.0] <= 1
 contribution[0,3,51.0] <= 1
 contribution[0,3,53.0] <= 1
 contribution[0,3,54.0] <= 1
 contribution[0,3,56.0] <= 1
 contribution[0,3,57.0] <= 1
 contribution[0,3,62.0] <= 1
 contribution[0,3,65.0] <= 1
 contribution[0,3,75.0] <= 1
 contribution[0,3,76.0] <= 1
 contribution[0,3,85.0] <= 1
 contribution[0,3,86.0] <= 1
 contribution[0,3,88.0] <= 1
 contribution[0,3,94.0] <= 1
 contribution[0,4,0.0] <= 1
 contribution[0,4,2.0] <= 1
 contribution[0,4,6.0] <= 1
 contribution[0,4,9.0] <= 1
 contribution[0,4,13.0] <= 1
 contribution[0,4,16.0] <= 1
 contribution[0,4,17.0] <= 1
 contribution[0,4,19.0] <= 1
 contribution[0,4,22.0] <= 1
 contribution[0,4,24.0] <= 1
 contribution[0,4,30.0] <= 1
 contribution[0,4,36.0] <= 1
 contribution[0,4,38.0] <= 1
 contribution[0,4,40.0] <= 1
 contribution[0,4,41.0] <= 1
 contribution[0,4,42.0] <= 1
 contribution[0,4,43.0] <= 1
 contribution[0,4,45.0] <= 1
 contribution[0,4,47.0] <= 1
 contribution[0,4,48.0] <= 1
 contribution[0,4,52.0] <= 1
 contribution[0,4,54.0] <= 1
 contribution[0,4,56.0] <= 1
 contribution[0,4,59.0] <= 1
 contribution[0,4,62.0] <= 1
 contribution[0,4,64.0] <= 1
 contribution[0,4,67.0] <= 1
 contribution[0,4,68.0] <= 1
 contribution[0,4,76.0] <= 1
 contribution[0,4,88.0] <= 1
 contribution[0,4,94.0] <= 1
 contribution[0,4,99.0] <= 1
 contribution[1,0,1.0] <= 1
 contribution[1,0,3.0] <= 1
 contribution[1,0,5.0] <= 1
 contribution[1,0,10.0] <= 1
 contribution[1,0,11.0] <= 1
 contribution[1,0,16.0] <= 1
 contribution[1,0,19.0] <= 1
 contribution[1,0,22.0] <= 1
 contribution[1,0,30.0] <= 1
 contribution[1,0,36.0] <= 1
 contribution[1,0,37.0] <= 1
 contribution[1,0,38.0] <= 1
 contribution[1,0,40.0] <= 1
 contribution[1,0,41.0] <= 1
 contribution[1,0,47.0] <= 1
 contribution[1,0,49.0] <= 1
 contribution[1,0,54.0] <= 1
 contribution[1,0,56.0] <= 1
 contribution[1,0,58.0] <= 1
 contribution[1,0,59.0] <= 1
 contribution[1,0,60.0] <= 1
 contribution[1,0,64.0] <= 1
 contribution[1,0,66.0] <= 1
 contribution[1,0,68.0] <= 1
 contribution[1,0,70.0] <= 1
 contribution[1,0,71.0] <= 1
 contribution[1,0,73.0] <= 1
 contribution[1,0,83.0] <= 1
 contribution[1,0,85.0] <= 1
 contribution[1,0,86.0] <= 1
 contribution[1,0,91.0] <= 1
 contribution[1,0,92.0] <= 1
 contribution[1,0,93.0] <= 1
 contribution[1,0,95.0] <= 1
 contribution[1,0,96.0] <= 1
 contribution[1,0,99.0] <= 1
 contribution[1,1,5.0] <= 1
 contribution[1,1,6.0] <= 1
 contribution[1,1,8.0] <= 1
 contribution[1,1,17.0] <= 1
 contribution[1,1,36.0] <= 1
 contribution[1,1,38.0] <= 1
 contribution[1,1,41.0] <= 1
 contribution[1,1,46.0] <= 1
 contribution[1,1,48.0] <= 1
 contribution[1,1,52.0] <= 1
 contribution[1,1,53.0] <= 1
 contribution[1,1,54.0] <= 1
 contribution[1,1,55.0] <= 1
 contribution[1,1,56.0] <= 1
 contribution[1,1,57.0] <= 1
 contribution[1,1,61.0] <= 1
 contribution[1,1,63.0] <= 1
 contribution[1,1,65.0] <= 1
 contribution[1,1,68.0] <= 1
 contribution[1,1,72.0] <= 1
 contribution[1,1,76.0] <= 1
 contribution[1,1,80.0] <= 1
 contribution[1,1,81.0] <= 1
 contribution[1,1,82.0] <= 1
 contribution[1,1,84.0] <= 1
 contribution[1,1,86.0] <= 1
 contribution[1,1,87.0] <= 1
 contribution[1,1,91.0] <= 1
 contribution[1,1,92.0] <= 1
 contribution[1,1,94.0] <= 1
 contribution[1,1,95.0] <= 1
 contribution[1,1,96.0] <= 1
 contribution[1,1,100.0] <= 1
 contribution[1,2,3.0] <= 1
 contribution[1,2,4.0] <= 1
 contribution[1,2,7.0] <= 1
 contribution[1,2,9.0] <= 1
 contribution[1,2,12.0] <= 1
 contribution[1,2,13.0] <= 1
 contribution[1,2,14.0] <= 1
 contribution[1,2,26.0] <= 1
 contribution[1,2,27.0] <= 1
 contribution[1,2,28.0] <= 1
 contribution[1,2,29.0] <= 1
 contribution[1,2,37.0] <= 1
 contribution[1,2,50.0] <= 1
 contribution[1,2,56.0] <= 1
 contribution[1,2,57.0] <= 1
 contribution[1,2,60.0] <= 1
 contribution[1,2,61.0] <= 1
 contribution[1,2,66.0] <= 1
 contribution[1,2,69.0] <= 1
 contribution[1,2,73.0] <= 1
 contribution[1,2,76.0] <= 1
 contribution[1,2,77.0] <= 1
 contribution[1,2,84.0] <= 1
 contribution[1,2,86.0] <= 1
 contribution[1,2,87.0] <= 1
 contribution[1,2,88.0] <= 1
 contribution[1,2,90.0] <= 1
 contribution[1,2,91.0] <= 1
 contribution[1,2,93.0] <= 1
 contribution[1,2,97.0] <= 1
 contribution[1,2,98.0] <= 1
 contribution[1,2,99.0] <= 1
 contribution[1,2,100.0] <= 1
 contribution[1,3,2.0] <= 1
 contribution[1,3,6.0] <= 1
 contribution[1,3,13.0] <= 1
 contribution[1,3,19.0] <= 1
 contribution[1,3,23.0] <= 1
 contribution[1,3,26.0] <= 1
 contribution[1,3,34.0] <= 1
 contribution[1,3,35.0] <= 1
 contribution[1,3,36.0] <= 1
 contribution[1,3,37.0] <= 1
 contribution[1,3,38.0] <= 1
 contribution[1,3,39.0] <= 1
 contribution[1,3,41.0] <= 1
 contribution[1,3,43.0] <= 1
 contribution[1,3,44.0] <= 1
 contribution[1,3,47.0] <= 1
 contribution[1,3,48.0] <= 1
 contribution[1,3,51.0] <= 1
 contribution[1,3,54.0] <= 1
 contribution[1,3,55.0] <= 1
 contribution[1,3,56.0] <= 1
 contribution[1,3,60.0] <= 1
 contribution[1,3,63.0] <= 1
 contribution[1,3,65.0] <= 1
 contribution[1,3,68.0] <= 1
 contribution[1,3,71.0] <= 1
 contribution[1,3,73.0] <= 1
 contribution[1,3,75.0] <= 1
 contribution[1,3,77.0] <= 1
 contribution[1,3,80.0] <= 1
 contribution[1,3,85.0] <= 1
 contribution[1,3,86.0] <= 1
 contribution[1,3,94.0] <= 1
 contribution[1,4,0.0] <= 1
 contribution[1,4,6.0] <= 1
 contribution[1,4,9.0] <= 1
 contribution[1,4,10.0] <= 1
 contribution[1,4,13.0] <= 1
 contribution[1,4,16.0] <= 1
 contribution[1,4,17.0] <= 1
 contribution[1,4,19.0] <= 1
 contribution[1,4,30.0] <= 1
 contribution[1,4,36.0] <= 1
 contribution[1,4,38.0] <= 1
 contribution[1,4,40.0] <= 1
 contribution[1,4,41.0] <= 1
 contribution[1,4,42.0] <= 1
 contribution[1,4,43.0] <= 1
 contribution[1,4,45.0] <= 1
 contribution[1,4,47.0] <= 1
 contribution[1,4,48.0] <= 1
 contribution[1,4,50.0] <= 1
 contribution[1,4,52.0] <= 1
 contribution[1,4,59.0] <= 1
 contribution[1,4,60.0] <= 1
 contribution[1,4,62.0] <= 1
 contribution[1,4,63.0] <= 1
 contribution[1,4,64.0] <= 1
 contribution[1,4,65.0] <= 1
 contribution[1,4,67.0] <= 1
 contribution[1,4,70.0] <= 1
 contribution[1,4,75.0] <= 1
 contribution[1,4,78.0] <= 1
 contribution[1,4,81.0] <= 1
 contribution[1,4,82.0] <= 1
 contribution[1,4,83.0] <= 1
 contribution[1,4,88.0] <= 1
Binaries
 delta[0,0,3.0] delta[0,0,5.0] delta[0,0,10.0] delta[0,0,11.0]
 delta[0,0,19.0] delta[0,0,20.0] delta[0,0,22.0] delta[0,0,25.0]
 delta[0,0,26.0] delta[0,0,30.0] delta[0,0,32.0] delta[0,0,33.0]
 delta[0,0,37.0] delta[0,0,38.0] delta[0,0,40.0] delta[0,0,42.0]
 delta[0,0,45.0] delta[0,0,46.0] delta[0,0,47.0] delta[0,0,49.0]
 delta[0,0,56.0] delta[0,0,59.0] delta[0,0,60.0] delta[0,0,62.0]
 delta[0,0,66.0] delta[0,0,69.0] delta[0,0,73.0] delta[0,0,81.0]
 delta[0,0,83.0] delta[0,0,85.0] delta[0,0,86.0] delta[0,0,90.0]
 delta[0,0,91.0] delta[0,0,93.0] delta[0,0,99.0] delta[0,1,2.0]
 delta[0,1,5.0] delta[0,1,6.0] delta[0,1,8.0] delta[0,1,9.0]
 delta[0,1,12.0] delta[0,1,16.0] delta[0,1,17.0] delta[0,1,23.0]
 delta[0,1,27.0] delta[0,1,29.0] delta[0,1,32.0] delta[0,1,33.0]
 delta[0,1,34.0] delta[0,1,36.0] delta[0,1,38.0] delta[0,1,41.0]
 delta[0,1,46.0] delta[0,1,48.0] delta[0,1,50.0] delta[0,1,52.0]
 delta[0,1,53.0] delta[0,1,54.0] delta[0,1,56.0] delta[0,1,61.0]
 delta[0,1,68.0] delta[0,1,72.0] delta[0,1,73.0] delta[0,1,82.0]
 delta[0,1,84.0] delta[0,1,87.0] delta[0,1,94.0] delta[0,1,95.0]
 delta[0,1,100.0] delta[0,2,3.0] delta[0,2,4.0] delta[0,2,7.0]
 delta[0,2,9.0] delta[0,2,12.0] delta[0,2,13.0] delta[0,2,21.0]
 delta[0,2,23.0] delta[0,2,27.0] delta[0,2,29.0] delta[0,2,37.0]
 delta[0,2,38.0] delta[0,2,40.0] delta[0,2,43.0] delta[0,2,55.0]
 delta[0,2,60.0] delta[0,2,66.0] delta[0,2,69.0] delta[0,2,72.0]
 delta[0,2,73.0] delta[0,2,74.0] delta[0,2,76.0] delta[0,2,77.0]
 delta[0,2,78.0] delta[0,2,80.0] delta[0,2,84.0] delta[0,2,88.0]
 delta[0,2,93.0] delta[0,2,97.0] delta[0,2,99.0] delta[0,2,100.0]
 delta[0,3,0.0] delta[0,3,2.0] delta[0,3,13.0] delta[0,3,18.0]
 delta[0,3,19.0] delta[0,3,23.0] delta[0,3,26.0] delta[0,3,31.0]
 delta[0,3,33.0] delta[0,3,35.0] delta[0,3,36.0] delta[0,3,37.0]
 delta[0,3,38.0] delta[0,3,39.0] delta[0,3,41.0] delta[0,3,43.0]
 delta[0,3,44.0] delta[0,3,47.0] delta[0,3,48.0] delta[0,3,51.0]
 delta[0,3,53.0] delta[0,3,54.0] delta[0,3,56.0] delta[0,3,57.0]
 delta[0,3,62.0] delta[0,3,65.0] delta[0,3,75.0] delta[0,3,76.0]
 delta[0,3,85.0] delta[0,3,86.0] delta[0,3,88.0] delta[0,3,94.0]
 delta[0,4,0.0] delta[0,4,2.0] delta[0,4,6.0] delta[0,4,9.0]
 delta[0,4,13.0] delta[0,4,16.0] delta[0,4,17.0] delta[0,4,19.0]
 delta[0,4,22.0] delta[0,4,24.0] delta[0,4,30.0] delta[0,4,36.0]
 delta[0,4,38.0] delta[0,4,40.0] delta[0,4,41.0] delta[0,4,42.0]
 delta[0,4,43.0] delta[0,4,45.0] delta[0,4,47.0] delta[0,4,48.0]
 delta[0,4,52.0] delta[0,4,54.0] delta[0,4,56.0] delta[0,4,59.0]
 delta[0,4,62.0] delta[0,4,64.0] delta[0,4,67.0] delta[0,4,68.0]
 delta[0,4,76.0] delta[0,4,88.0] delta[0,4,94.0] delta[0,4,99.0]
 delta[1,0,1.0] delta[1,0,3.0] delta[1,0,5.0] delta[1,0,10.0]
 delta[1,0,11.0] delta[1,0,16.0] delta[1,0,19.0] delta[1,0,22.0]
 delta[1,0,30.0] delta[1,0,36.0] delta[1,0,37.0] delta[1,0,38.0]
 delta[1,0,40.0] delta[1,0,41.0] delta[1,0,47.0] delta[1,0,49.0]
 delta[1,0,54.0] delta[1,0,56.0] delta[1,0,58.0] delta[1,0,59.0]
 delta[1,0,60.0] delta[1,0,64.0] delta[1,0,66.0] delta[1,0,68.0]
 delta[1,0,70.0] delta[1,0,71.0] delta[1,0,73.0] delta[1,0,83.0]
 delta[1,0,85.0] delta[1,0,86.0] delta[1,0,91.0] delta[1,0,92.0]
 delta[1,0,93.0] delta[1,0,95.0] delta[1,0,96.0] delta[1,0,99.0]
 delta[1,1,5.0] delta[1,1,6.0] delta[1,1,8.0] delta[1,1,17.0]
 delta[1,1,36.0] delta[1,1,38.0] delta[1,1,41.0] delta[1,1,46.0]
 delta[1,1,48.0] delta[1,1,52.0] delta[1,1,53.0] delta[1,1,54.0]
 delta[1,1,55.0] delta[1,1,56.0] delta[1,1,57.0] delta[1,1,61.0]
 delta[1,1,63.0] delta[1,1,65.0] delta[1,1,68.0] delta[1,1,72.0]
 delta[1,1,76.0] delta[1,1,80.0] delta[1,1,81.0] delta[1,1,82.0]
 delta[1,1,84.0] delta[1,1,86.0] delta[1,1,87.0] delta[1,1,91.0]
 delta[1,1,92.0] delta[1,1,94.0] delta[1,1,95.0] delta[1,1,96.0]
 delta[1,1,100.0] delta[1,2,3.0] delta[1,2,4.0] delta[1,2,7.0]
 delta[1,2,9.0] delta[1,2,12.0] delta[1,2,13.0] delta[1,2,14.0]
 delta[1,2,26.0] delta[1,2,27.0] delta[1,2,28.0] delta[1,2,29.0]
 delta[1,2,37.0] delta[1,2,50.0] delta[1,2,56.0] delta[1,2,57.0]
 delta[1,2,60.0] delta[1,2,61.0] delta[1,2,66.0] delta[1,2,69.0]
 delta[1,2,73.0] delta[1,2,76.0] delta[1,2,77.0] delta[1,2,84.0]
 delta[1,2,86.0] delta[1,2,87.0] delta[1,2,88.0] delta[1,2,90.0]
 delta[1,2,91.0] delta[1,2,93.0] delta[1,2,97.0] delta[1,2,98.0]
 delta[1,2,99.0] delta[1,2,100.0] delta[1,3,2.0] delta[1,3,6.0]
 delta[1,3,13.0] delta[1,3,19.0] delta[1,3,23.0] delta[1,3,26.0]
 delta[1,3,34.0] delta[1,3,35.0] delta[1,3,36.0] delta[1,3,37.0]
 delta[1,3,38.0] delta[1,3,39.0] delta[1,3,41.0] delta[1,3,43.0]
 delta[1,3,44.0] delta[1,3,47.0] delta[1,3,48.0] delta[1,3,51.0]
 delta[1,3,54.0] delta[1,3,55.0] delta[1,3,56.0] delta[1,3,60.0]
 delta[1,3,63.0] delta[1,3,65.0] delta[1,3,68.0] delta[1,3,71.0]
 delta[1,3,73.0] delta[1,3,75.0] delta[1,3,77.0] delta[1,3,80.0]
 delta[1,3,85.0] delta[1,3,86.0] delta[1,3,94.0] delta[1,4,0.0]
 delta[1,4,6.0] delta[1,4,9.0] delta[1,4,10.0] delta[1,4,13.0]
 delta[1,4,16.0] delta[1,4,17.0] delta[1,4,19.0] delta[1,4,30.0]
 delta[1,4,36.0] delta[1,4,38.0] delta[1,4,40.0] delta[1,4,41.0]
 delta[1,4,42.0] delta[1,4,43.0] delta[1,4,45.0] delta[1,4,47.0]
 delta[1,4,48.0] delta[1,4,50.0] delta[1,4,52.0] delta[1,4,59.0]
 delta[1,4,60.0] delta[1,4,62.0] delta[1,4,63.0] delta[1,4,64.0]
 delta[1,4,65.0] delta[1,4,67.0] delta[1,4,70.0] delta[1,4,75.0]
 delta[1,4,78.0] delta[1,4,81.0] delta[1,4,82.0] delta[1,4,83.0]
 delta[1,4,88.0] error[0] error[1] error[2] error[3] error[4] error[5]
 error[6] error[7] error[8] error[9] error[10] error[11] error[12]
 error[13] error[14] error[15] error[16] error[17] error[18] error[19]
 error[20] error[21] error[22] error[23] error[24] error[25] error[26]
 error[27] error[28] error[29] error[30] error[31] error[32] error[33]
 error[34] error[35] error[36] error[37] error[38] error[39] error[40]
 error[41] error[42] error[43] error[44] error[45] error[46] error[47]
 error[48] error[49] error[50] error[51] error[52] error[53] error[54]
 error[55] error[56] error[57] error[58] error[59]
End

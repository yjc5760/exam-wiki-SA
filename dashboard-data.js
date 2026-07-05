// exam-wiki-SA 儀表板資料檔
// 由 question_index.json 與 syllabus_taxonomy.json 生成。索引或命題大綱更新後，對 Cowork 說「更新儀表板資料」即可重新生成。
// 格式：[moduleId, primaryTopicId(縮寫，去SA-前綴), secondaryTopicIds, viz檔名前綴陣列, tags, pdf補充筆記檔名陣列]
// pdf 欄位：掃描 raw/solutions/SA-XXXX-N/ 下所有 *.pdf（原始檔名，含副檔名），由 REFRESH-DASHBOARD 指令維護
window.SA_TOPICS = {
  "U1-1": "靜不定度與穩定性之判斷",
  "U1-2": "靜定結構之分析",
  "U1-3": "靜定及靜不定結構影響線",
  "U2-1": "靜不定結構最小功法",
  "U2-2": "靜不定結構諧合變位",
  "U2-3": "靜不定結構之傾角變位法",
  "U2-4": "靜不定結構之矩陣分析法",
  "U2-5": "彎矩分配法",
  "U3-1": "建築結構系統之使用",
  "U3-2": "建築結構系統分析"
};
window.SA_UNITS = {
  "U1": "第一單元：靜定結構分析",
  "U2": "第二單元：靜不定結構分析",
  "U3": "第三單元：建築結構系統"
};
// 題目資料（初始為空，說「更新儀表板資料」後由 REFRESH-DASHBOARD 填入）
window.SA_QUESTIONS = [];

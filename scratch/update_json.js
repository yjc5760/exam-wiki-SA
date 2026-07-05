const fs = require('fs');
const data = JSON.parse(fs.readFileSync('raw/json/question_index.json', 'utf8'));
// 確保不重複新增
if (!data.questions.find(q => q.moduleId === 'SA-2021-1')) {
  data.questions.push({
    moduleId: "SA-2021-1",
    year: 2021,
    rocYear: 110,
    questionNumber: 1,
    primaryTopicId: "SA-U2-3",
    primaryTopicName: "靜不定結構之傾角變位法",
    secondaryTopicIds: [],
    verificationStatus: "unverified",
    hasSolution: true,
    hasViz: true,
    hasHandwritten: false,
    tags: ["傾角變位法", "彈簧支承", "內部鉸", "剛度等效", "連續梁"]
  });
  // 按照年份與題號降序排列 (選用，為了美觀)
  data.questions.sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year;
    return b.questionNumber - a.questionNumber;
  });
  fs.writeFileSync('raw/json/question_index.json', JSON.stringify(data, null, 2));
}
console.log('JSON updated successfully.');

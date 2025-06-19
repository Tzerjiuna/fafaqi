/*const fs = require("fs");
const path = require("path");

function extractProductsFromDir(folderName) {
  const directory = path.join(__dirname, "网页", folderName);
  const outputFile = path.join(__dirname, `${folderName}.json`);

  function getExistingData() {
    try {
      if (!fs.existsSync(outputFile)) return [];
      const fileContent = fs.readFileSync(outputFile, "utf-8").trim();
      if (!fileContent) return [];
      const parsed = JSON.parse(fileContent);
      return Array.isArray(parsed) ? parsed : [];
    } catch (err) {
      console.error(`❌ 读取 ${folderName}.json 出错:`, err.message);
      return [];
    }
  }

  function extractNewProducts() {
    const newResults = [];

    fs.readdirSync(directory)
      .filter((file) => file.endsWith(".aspx"))
      .forEach((file) => {
        try {
          const content = fs.readFileSync(path.join(directory, file), "utf-8");
          const productRegex = /"@type":"Product"(.*?)"availability":"https:\/\/schema\.org\/InStock"}/gs;

          let match;
          while ((match = productRegex.exec(content)) !== null) {
            const block = match[1];
            const images = [...block.matchAll(/"https:\/\/cdn-images\.farfetch-contents\.com\/.*?\.jpg"/g)]
              .map((m) => m[0].replace(/"/g, ""));

            if (images.length) {
              newResults.push({
                title: block.match(/"brand":\{"@type":"Brand","name":"(.*?)"\}/)?.[1] || "",
                description: block.match(/"name":"(.*?)"/)?.[1] || "",
                price: parseFloat(block.match(/"price":(\d+(\.\d+)?)/)?.[1]) || null,
                images,
                categories: folderName
              });
            }
          }
        } catch (err) {
          console.error(`❌ 处理文件 ${file} 出错:`, err.message);
        }
      });

    return newResults;
  }

  const existingData = getExistingData();
  const newResults = extractNewProducts();

  const mergedData = existingData.concat(newResults);
  const uniqueData = mergedData.filter(
    (item, index, self) =>
      index === self.findIndex((t) => t.description === item.description && t.description)
  );

  try {
    fs.writeFileSync(outputFile, JSON.stringify(uniqueData, null, 2));
    console.log(`✅ [${folderName}] 新增 ${newResults.length} 条，总计 ${uniqueData.length} 条`);
  } catch (err) {
    console.error(`❌ 保存 ${folderName}.json 失败:`, err.message);
  }
}

// 自动遍历网页目录下所有文件夹并提取
const rootDir = path.join(__dirname, "网页");

fs.readdirSync(rootDir, { withFileTypes: true })
  .filter(dirent => dirent.isDirectory())
  .forEach(dirent => {
    extractProductsFromDir(dirent.name);
  });
*/


const fs = require("fs");
const path = require("path");

const folderName = "women"; // ✅ 固定为 women
const directory = path.join(__dirname, "网页", folderName);
const outputFile = path.join(__dirname, `${folderName}.json`);

function getExistingData() {
  try {
    if (!fs.existsSync(outputFile)) return [];
    const fileContent = fs.readFileSync(outputFile, "utf-8").trim();
    if (!fileContent) return [];
    const parsed = JSON.parse(fileContent);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    console.error(`❌ 读取 ${folderName}.json 出错:`, err.message);
    return [];
  }
}

function extractNewProducts() {
  const newResults = [];

  fs.readdirSync(directory)
    .filter((file) => file.endsWith(".aspx"))
    .forEach((file) => {
      try {
        const content = fs.readFileSync(path.join(directory, file), "utf-8");
        const productRegex = /"@type":"Product"(.*?)"availability":"https:\/\/schema\.org\/InStock"}/gs;

        let match;
        while ((match = productRegex.exec(content)) !== null) {
          const block = match[1];
          const images = [...block.matchAll(/"https:\/\/cdn-images\.farfetch-contents\.com\/.*?\.jpg"/g)]
            .map((m) => m[0].replace(/"/g, ""));

          if (images.length) {
            newResults.push({
              title: block.match(/"brand":\{"@type":"Brand","name":"(.*?)"\}/)?.[1] || "",
              description: block.match(/"name":"(.*?)"/)?.[1] || "",
              price: parseFloat(block.match(/"price":(\d+(\.\d+)?)/)?.[1]) || null,
              images,
              categories: folderName
            });
          }
        }
      } catch (err) {
        console.error(`❌ 处理文件 ${file} 出错:`, err.message);
      }
    });

  return newResults;
}

const existingData = getExistingData();
const newResults = extractNewProducts();

const mergedData = existingData.concat(newResults);
const uniqueData = mergedData.filter(
  (item, index, self) =>
    index === self.findIndex((t) => t.description === item.description && t.description)
);

try {
  fs.writeFileSync(outputFile, JSON.stringify(uniqueData, null, 2));
  console.log(`✅ [${folderName}] 新增 ${newResults.length} 条，总计 ${uniqueData.length} 条`);
} catch (err) {
  console.error(`❌ 保存 ${folderName}.json 失败:`, err.message);
}

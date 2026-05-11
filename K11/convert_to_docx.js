const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType } = require('docx');
const fs = require('fs');

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

// 解析Markdown表格
function parseTable(markdownTable) {
    const lines = markdownTable.trim().split('\n');
    const rows = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line || line.startsWith('|') === false) continue;
        
        // 跳过对齐行
        if (line.includes('---')) continue;
        
        const cells = line.split('|').filter(cell => cell.trim() !== '');
        const cellTexts = cells.map(cell => {
            let text = cell.trim();
            // 处理粗体
            text = text.replace(/\*\*(.+?)\*\*/g, '$1');
            // 处理斜体
            text = text.replace(/\*(.+?)\*/g, '$1');
            return text;
        });
        rows.push(cellTexts);
    }
    return rows;
}

// 获取总列数
function getColumnCount(rows) {
    return Math.max(...rows.map(row => row.length));
}

// 估算列宽
function calculateColumnWidths(rows) {
    const colCount = getColumnCount(rows);
    const totalWidth = 9000;
    const colWidth = Math.floor(totalWidth / colCount);
    return Array(colCount).fill(colWidth);
}

// 创建表格
function createTable(rows) {
    if (rows.length === 0) return null;
    
    const colCount = getColumnCount(rows);
    const colWidths = calculateColumnWidths(rows);
    
    const tableRows = rows.map((row, rowIndex) => {
        const cells = [];
        for (let i = 0; i < colCount; i++) {
            const cellText = row[i] || '';
            const isHeader = rowIndex === 0;
            
            cells.push(new TableCell({
                borders: cellBorders,
                width: { size: colWidths[i], type: WidthType.DXA },
                shading: isHeader ? { fill: "E8E8E8", type: ShadingType.CLEAR } : undefined,
                children: [new Paragraph({ 
                    children: [new TextRun({ 
                        text: cellText,
                        bold: isHeader,
                        size: 22 
                    })]
                })]
            }));
        }
        return new TableRow({ 
            tableHeader: rowIndex === 0,
            children: cells 
        });
    });
    
    return new Table({
        columnWidths: colWidths,
        rows: tableRows
    });
}

// 解析内容并生成docx元素
function parseContent(markdown) {
    const lines = markdown.split('\n');
    const elements = [];
    let i = 0;
    let tableBuffer = [];
    let inTable = false;
    
    while (i < lines.length) {
        const line = lines[i];
        
        // 检测表格开始
        if (line.includes('|') && line.trim().startsWith('|')) {
            inTable = true;
            tableBuffer.push(line);
            i++;
            continue;
        }
        
        // 表格行继续
        if (inTable && line.includes('|') && line.trim().startsWith('|')) {
            tableBuffer.push(line);
            i++;
            continue;
        }
        
        // 表格结束
        if (inTable && tableBuffer.length > 0) {
            const table = createTable(parseTable(tableBuffer.join('\n')));
            if (table) elements.push(table);
            tableBuffer = [];
            inTable = false;
            continue;
        }
        
        // 标题
        if (line.startsWith('# ')) {
            elements.push(new Paragraph({
                heading: HeadingLevel.TITLE,
                children: [new TextRun({ text: line.substring(2), bold: true, size: 48 })]
            }));
        } else if (line.startsWith('## ')) {
            elements.push(new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun({ text: line.substring(3), bold: true, size: 32 })]
            }));
        } else if (line.startsWith('### ')) {
            elements.push(new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun({ text: line.substring(4), bold: true, size: 26 })]
            }));
        }
        // 分隔线
        else if (line.trim() === '---') {
            elements.push(new Paragraph({
                spacing: { before: 200, after: 200 },
                border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "CCCCCC" } },
                children: [new TextRun({ text: "" })]
            }));
        }
        // 引用
        else if (line.startsWith('> ')) {
            elements.push(new Paragraph({
                indent: { left: 720 },
                shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
                children: [new TextRun({ text: line.substring(2), italics: true })]
            }));
        }
        // 有序列表
        else if (/^\d+\.\s/.test(line)) {
            const text = line.replace(/^\d+\.\s/, '');
            elements.push(new Paragraph({
                numbering: { reference: "ordered-list", level: 0 },
                children: [new TextRun({ text: text })]
            }));
        }
        // 无序列表
        else if (line.startsWith('- ') || line.startsWith('* ')) {
            const text = line.substring(2);
            elements.push(new Paragraph({
                numbering: { reference: "bullet-list", level: 0 },
                children: [new TextRun({ text: text })]
            }));
        }
        // 普通段落（包含emoji的）
        else if (line.trim()) {
            // 处理粗体
            const text = line;
            const runs = [];
            let remaining = text;
            
            while (remaining) {
                const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
                if (boldMatch && boldMatch.index === 0) {
                    runs.push(new TextRun({ text: boldMatch[1], bold: true }));
                    remaining = remaining.substring(boldMatch[0].length);
                } else if (boldMatch) {
                    runs.push(new TextRun({ text: remaining.substring(0, boldMatch.index) }));
                    remaining = remaining.substring(boldMatch.index);
                } else {
                    runs.push(new TextRun({ text: remaining }));
                    break;
                }
            }
            
            if (runs.length === 0) {
                runs.push(new TextRun({ text: text }));
            }
            
            elements.push(new Paragraph({
                spacing: { after: 100 },
                children: runs.length > 0 ? runs : [new TextRun({ text: text })]
            }));
        }
        // 空行
        else {
            elements.push(new Paragraph({ children: [new TextRun({ text: "" })] }));
        }
        
        i++;
    }
    
    // 处理最后的表格
    if (tableBuffer.length > 0) {
        const table = createTable(parseTable(tableBuffer.join('\n')));
        if (table) elements.push(table);
    }
    
    return elements;
}

// 创建文档
const doc = new Document({
    styles: {
        default: { document: { run: { font: "Arial", size: 22 } } },
        paragraphStyles: [
            { id: "Title", name: "Title", basedOn: "Normal",
              run: { size: 48, bold: true, color: "000000", font: "Arial" },
              paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 32, bold: true, color: "000000", font: "Arial" },
              paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 26, bold: true, color: "000000", font: "Arial" },
              paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 1 } }
        ]
    },
    numbering: {
        config: [
            { reference: "bullet-list",
              levels: [{ level: 0, format: "bullet", text: "•", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
            { reference: "ordered-list",
              levels: [{ level: 0, format: "decimal", text: "%1.", alignment: AlignmentType.LEFT,
                style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
        ]
    },
    sections: [{
        properties: {
            page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
        },
        children: parseContent(fs.readFileSync('/app/data/所有对话/主对话/geo-insight/K11/武汉K11_GEO报告_公众号版.md', 'utf8'))
    }]
});

// 保存文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('/app/data/所有对话/主对话/geo-insight/K11/武汉K11_GEO报告_公众号版.docx', buffer);
    console.log('文档已成功创建: /app/data/所有对话/主对话/geo-insight/K11/武汉K11_GEO报告_公众号版.docx');
});

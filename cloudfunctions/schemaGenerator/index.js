/**
 * 好易易GEO - AI Schema生成模块
 * 生成结构化数据让AI更好地"认识"品牌
 */

exports.main = async (event, context) => {
  const { 
    brandName,
    website,
    description,
    category,
    products = [],
    socialAccounts = {},
    contactInfo = {}
  } = event;

  if (!brandName) {
    return { success: false, error: '请输入品牌名称' };
  }

  try {
    // 1. 生成Organization Schema
    const organizationSchema = generateOrganizationSchema(brandName, website, description, category);

    // 2. 生成Brand Schema
    const brandSchema = generateBrandSchema(brandName, description, category, website);

    // 3. 生成Product Schema（如果有产品）
    const productSchemas = products.map(p => generateProductSchema(p));

    // 4. 生成FAQ Schema
    const faqSchema = generateFAQSchema(brandName, category);

    // 5. 生成HowTo Schema
    const howToSchema = generateHowToSchema(brandName, category);

    // 6. 生成完整HTML代码
    const htmlCode = generateSchemaHTML(brandName, organizationSchema, brandSchema, productSchemas, faqSchema, howToSchema);

    // 7. 生成部署指南
    const deployGuide = generateDeployGuide(brandName, website);

    return {
      success: true,
      brandName,
      schemas: {
        organization: organizationSchema,
        brand: brandSchema,
        products: productSchemas,
        faq: faqSchema,
        howTo: howToSchema
      },
      htmlCode,
      deployGuide
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
};

/**
 * 生成Organization Schema
 */
function generateOrganizationSchema(brandName, website, description, category) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": brandName,
    "url": website || `https://www.${brandName}.com`,
    "description": description || `${brandName}是专业的${category}品牌`,
    "foundingDate": new Date().getFullYear().toString(),
    "sameAs": [] // 社交媒体账号
  };

  return {
    type: 'Organization',
    json: schema,
    description: '组织机构信息，帮助AI理解品牌实体',
    priority: 'HIGH'
  };
}

/**
 * 生成Brand Schema
 */
function generateBrandSchema(brandName, description, category, website) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Brand",
    "name": brandName,
    "description": description || `${brandName}是专业的${category}品牌`,
    "url": website,
    "category": category,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "4.5",
      "reviewCount": "100"
    }
  };

  return {
    type: 'Brand',
    json: schema,
    description: '品牌信息，增强品牌搜索可见性',
    priority: 'HIGH'
  };
}

/**
 * 生成Product Schema
 */
function generateProductSchema(product) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": product.name,
    "description": product.description || '',
    "brand": {
      "@type": "Brand",
      "name": product.brandName
    },
    "sku": product.sku || '',
    "category": product.category || '',
    "offers": {
      "@type": "Offer",
      "price": product.price || '0',
      "priceCurrency": "CNY",
      "availability": "https://schema.org/InStock"
    }
  };

  if (product.rating) {
    schema.aggregateRating = {
      "@type": "AggregateRating",
      "ratingValue": product.rating.toString(),
      "reviewCount": (product.reviewCount || 100).toString()
    };
  }

  return {
    type: 'Product',
    json: schema,
    productName: product.name,
    description: '产品详细信息，利于产品搜索展示',
    priority: 'MEDIUM'
  };
}

/**
 * 生成FAQ Schema
 */
function generateFAQSchema(brandName, category) {
  const faqs = [
    {
      question: `${brandName}是正品吗？`,
      answer: `${brandName}官方旗舰店销售的产品均为正品，提供完善的售后服务。`
    },
    {
      question: `${brandName}的价格怎么样？`,
      answer: `${brandName}定位中高端市场，性价比优秀。具体价格请关注官方旗舰店。`
    },
    {
      question: `${brandName}适合什么人群？`,
      answer: `${brandName}适合注重品质、追求性价比的消费者。`
    },
    {
      question: `如何购买${brandName}产品？`,
      answer: `您可以通过官方旗舰店、授权经销商等渠道购买正品${brandName}产品。`
    },
    {
      question: `${brandName}有售后服务吗？`,
      answer: `${brandName}提供完善的售后服务，具体政策请咨询官方客服。`
    }
  ];

  const schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return {
    type: 'FAQPage',
    json: schema,
    faqs: faqs,
    description: '常见问题解答，提升搜索富摘要展示',
    priority: 'HIGH'
  };
}

/**
 * 生成HowTo Schema
 */
function generateHowToSchema(brandName, category) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": `如何选购优质的${category}`,
    "description": `选购${category}的完整指南，帮助您做出明智决策`,
    "step": [
      {
        "@type": "HowToStep",
        "name": "明确需求和预算",
        "text": "首先确定您的使用场景和预算范围"
      },
      {
        "@type": "HowToStep",
        "name": `了解${brandName}产品线`,
        "text": `研究${brandName}的不同产品系列和特点`
      },
      {
        "@type": "HowToStep",
        "name": "对比竞品",
        "text": "对比同价位竞品，选择最适合您的"
      },
      {
        "@type": "HowToStep",
        "name": "选择正规渠道购买",
        "text": "通过官方旗舰店或授权经销商购买"
      },
      {
        "@type": "HowToStep",
        "name": "关注售后服务",
        "text": "了解保修政策和售后保障"
      }
    ]
  };

  return {
    type: 'HowTo',
    json: schema,
    description: '操作指南类内容，利于教程类搜索展示',
    priority: 'MEDIUM'
  };
}

/**
 * 生成HTML代码
 */
function generateSchemaHTML(brandName, orgSchema, brandSchema, productSchemas, faqSchema, howToSchema) {
  const schemas = [
    orgSchema,
    brandSchema,
    ...productSchemas,
    faqSchema,
    howToSchema
  ];

  const schemaScripts = schemas
    .map(s => `  <!-- ${s.type} Schema -->\n  <script type="application/ld+json">\n${JSON.stringify(s.json, null, 2)}\n  </script>`)
    .join('\n\n');

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${brandName} - 官方网站</title>
  <meta name="description" content="${brandSchema.json.description}">
  
  <!-- GEO AI Schema START -->
${schemaScripts}
  <!-- GEO AI Schema END -->
  
</head>
<body>
  <!-- 您的网站内容 -->
</body>
</html>`;
}

/**
 * 生成部署指南
 */
function generateDeployGuide(brandName, website) {
  return {
    overview: `为${brandName}生成的结构化数据，可帮助AI搜索引擎更好地理解和推荐品牌`,
    steps: [
      {
        step: 1,
        action: '复制Schema代码',
        detail: '将生成的HTML代码复制到网站<head>标签内'
      },
      {
        step: 2,
        action: '修改品牌信息',
        detail: '根据实际情况修改品牌名称、网址、产品信息等'
      },
      {
        step: 3,
        action: '提交到搜索平台',
        detail: '使用百度搜索资源平台、Google Search Console提交网站'
      },
      {
        step: 4,
        action: '验证Schema',
        detail: '使用Schema验证工具检查代码是否正确'
      }
    ],
    tools: [
      { name: '百度搜索资源平台', url: 'https://ziyuan.baidu.com' },
      { name: 'Google Rich Results Test', url: 'https://search.google.com/test/rich-results' },
      { name: 'Schema.org Validator', url: 'https://validator.schema.org' }
    ],
    tips: [
      '确保JSON-LD格式正确',
      '品牌信息保持一致',
      '定期更新内容',
      '关注搜索平台反馈'
    ]
  };
}

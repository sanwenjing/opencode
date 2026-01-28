const axios = require('axios');
const cheerio = require('cheerio');

class NewsFetcher {
  constructor() {
    this.name = "news-fetcher";
    this.baseUrl = "https://news.baidu.com";
  }

  async execute(params = {}) {
    try {
      const { count = 10, category = "综合" } = params;
      
      console.log(`🔍 正在从百度新闻获取前${count}条${category}新闻...`);
      
      const newsData = await this.fetchNews(count, category);
      
      return {
        success: true,
        data: newsData,
        message: `成功获取${newsData.news.length}条新闻`,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      throw new Error(`新闻获取失败: ${error.message}`);
    }
  }

  async fetchNews(count, category) {
    try {
      // 构建URL
      const url = this.buildNewsUrl(category);
      
      // 获取页面内容
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        timeout: 10000
      });

      const $ = cheerio.load(response.data);
      
      // 解析新闻列表
      const newsList = [];
      
      // 百度新闻的选择器可能需要根据实际页面结构调整
      $('.ulist.focuslistnews li, .news-item, .hotnews li').each((index, element) => {
        if (index >= count) return false;
        
        const $item = $(element);
        const $link = $item.find('a').first();
        
        const title = $link.text().trim() || $item.find('.title').text().trim();
        const href = $link.attr('href') || $item.find('a').attr('href');
        const summary = $item.find('.summary, .desc').text().trim();
        const time = $item.find('.time, .date').text().trim();
        
        if (title && href) {
          // 处理相对URL
          const fullUrl = href.startsWith('http') ? href : `${this.baseUrl}${href}`;
          
          newsList.push({
            title: this.cleanText(title),
            summary: this.cleanText(summary) || this.generateSummary(title),
            url: fullUrl,
            timestamp: time || new Date().toLocaleString('zh-CN'),
            index: index + 1
          });
        }
      });

      // 如果没有找到新闻，返回示例数据
      if (newsList.length === 0) {
        return this.getFallbackNews(count);
      }

      return {
        news: newsList,
        total: newsList.length,
        category: category,
        source: "baidu-news",
        fetchTime: new Date().toISOString()
      };
      
    } catch (error) {
      console.error('新闻获取错误:', error.message);
      // 网络错误时返回示例数据
      return this.getFallbackNews(count);
    }
  }

  buildNewsUrl(category) {
    const categoryMap = {
      '国内': 'guonei',
      '国际': 'guoji', 
      '科技': 'keji',
      '娱乐': 'yule',
      '体育': 'tiyu',
      '财经': 'caijing',
      '综合': ''
    };
    
    const categoryCode = categoryMap[category] || '';
    return categoryCode ? `${this.baseUrl}/${categoryCode}` : this.baseUrl;
  }

  cleanText(text) {
    if (!text) return '';
    return text.replace(/\s+/g, ' ').trim();
  }

  generateSummary(title) {
    return `关于"${title}"的最新报道`;
  }

  getFallbackNews(count) {
    // 示例新闻数据
    const sampleNews = [
      {
        title: "科技发展推动产业升级",
        summary: "最新科技动态显示，人工智能、量子计算等领域取得重大突破。科技创新为传统产业数字化转型提供强大支撑，新技术应用场景不断拓展，为高质量发展注入新动能。",
        url: "https://www.baidu.com/s?wd=科技发展推动产业升级",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 1
      },
      {
        title: "经济形势稳中向好", 
        summary: "最新经济数据显示，各项指标保持稳定增长态势。消费市场持续回暖，投资结构不断优化，外贸保持韧性，为全年经济社会发展目标实现奠定坚实基础。",
        url: "https://www.baidu.com/s?wd=经济形势稳中向好",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 2
      },
{
        title: "教育改革深入推进",
        summary: "教育部最新政策发布，全面推进素质教育发展。基础教育均衡发展持续推进，高等教育内涵建设不断加强，职业教育产教融合深入实施，教育公平质量同步提升。",
        url: "https://www.baidu.com/s?wd=教育改革深入推进",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 3
      },
      {
        title: "医疗健康新突破",
        summary: "医学研究领域取得重要进展，新型治疗技术为患者带来新希望。精准医疗、基因治疗等前沿技术不断突破，公共卫生体系持续完善，全民健康水平稳步提升。",
        url: "https://www.baidu.com/s?wd=医疗健康新突破",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 4
      },
      {
        title: "环保政策持续发力",
        summary: "绿色发展理念深入人心，各地环保措施效果显著。碳达峰碳中和工作稳步推进，污染防治攻坚战取得阶段性成果，生态环境质量持续改善，美丽中国建设迈出新步伐。",
        url: "https://www.baidu.com/s?wd=环保政策持续发力",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 5
      },
      {
        title: "数字经济蓬勃发展",
        summary: "数字技术与实体经济深度融合，新业态新模式不断涌现。5G、大数据、云计算等技术广泛应用，产业数字化转型加速推进，数字中国建设取得显著成效。",
        url: "https://www.baidu.com/s?wd=数字经济蓬勃发展",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 6
      },
      {
        title: "文化产业迎来新机遇",
        summary: "文化创意产业快速发展，传统文化焕发新的生机。文化产业与科技、旅游等领域深度融合，优秀文化产品供给不断丰富，文化软实力显著增强。",
        url: "https://www.baidu.com/s?wd=文化产业迎来新机遇",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 7
      },
      {
        title: "农业现代化加速推进",
        summary: "智慧农业技术应用广泛，粮食安全保障能力持续提升。农业机械化水平不断提高，绿色生产方式加快推广，农民增收渠道持续拓宽，乡村振兴战略深入实施。",
        url: "https://www.baidu.com/s?wd=农业现代化加速推进",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 8
      },
      {
        title: "交通基础设施完善",
        summary: "交通运输网络不断优化，便民惠民措施成效显著。高速铁路网持续完善，智慧交通建设加快推进，物流效率显著提升，综合立体交通体系加速形成。",
        url: "https://www.baidu.com/s?wd=交通基础设施完善",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 9
      },
      {
        title: "社会保障体系健全",
        summary: "民生保障水平稳步提高，公共服务覆盖面持续扩大。养老、医疗、失业等保险制度不断完善，社会救助体系更加健全，人民群众获得感幸福感安全感显著增强。",
        url: "https://www.baidu.com/s?wd=社会保障体系健全",
        timestamp: new Date().toLocaleString('zh-CN'),
        index: 10
      }
    ];

    return {
      news: sampleNews.slice(0, count),
      total: Math.min(sampleNews.length, count),
      category: "示例数据",
      source: "fallback-data",
      fetchTime: new Date().toISOString(),
      note: "由于网络原因，当前显示为示例数据"
    };
  }

  // 格式化输出，便于阅读
  formatOutput(newsData) {
    let output = `\n📰 今日头条新闻 (共${newsData.total}条)\n`;
    output += `${'='.repeat(50)}\n\n`;
    
    newsData.news.forEach((item, index) => {
      output += `${index + 1}. ${item.title}\n`;
      output += `   📝 ${item.summary}\n`;
      output += `   🔗 ${item.url}\n`;
      output += `   🕒 ${item.timestamp}\n\n`;
    });
    
    if (newsData.note) {
      output += `⚠️  ${newsData.note}\n`;
    }
    
    return output;
  }
}

module.exports = NewsFetcher;
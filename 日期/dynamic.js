const { HttpRequest } = require('./node/HttpRequest');
function strToJson(params) {
    let isJSON = str => {
        if (typeof str === 'string') {
            try {
                var obj = JSON.parse(str);
                if (typeof obj === 'object' && obj) {
                    return true;
                } else {
                    return false;
                }
            } catch (e) {
                console.error('error：' + str + '!!!' + e);
                return false;
            }
        }
        console.error('It is not a string!')
    }
    if (isJSON(params)) {
        let obj = JSON.parse(params);
        return obj
    }
}
function modifyDynamicRes (res){
    const jsonRes = strToJson(res),
        {data} = jsonRes;
    if (jsonRes.code !== 0) {
        console.warn('获取动态数据出错,可能是访问太频繁');
        return null;
    }
    /* 字符串防止损失精度 */
    const offset = typeof data.offset === 'string' ? data.offset : /(?<=next_offset":)[0-9]*/.exec(res)[0]
        , next = {
            has_more: data.has_more,
            next_offset: offset
        };
    /**
     * 储存获取到的一组动态中的信息
     */
    let array = [];
    if (next.has_more === 0) {
        console.log('动态数据读取完毕');
    } else {
        /**
         * 空动态无cards
         */
        const Cards = data.cards;
        Cards.forEach(onecard => {
            /**临时储存单个动态中的信息 */
            let obj = {};
            const {desc,card} = onecard
                , {info} = desc.user_profile
                , cardToJson = strToJson(card);
            obj.uid = info.uid; /* 转发者的UID */
            obj.uname = info.uname;/* 转发者的name */
            obj.rid_str = desc.rid_str;/* 用于发送评论 */
            obj.type = desc.type /* 动态类型 */
            obj.orig_type = desc.orig_type /* 源动态类型 */
            obj.dynamic_id = desc.dynamic_id_str; /* 转发者的动态ID !!!!此为大数需使用字符串值,不然JSON.parse()会有丢失精度 */
            const {extension} = onecard;
            obj.hasOfficialLottery = (typeof extension === 'undefined') ? false : typeof extension.lott === 'undefined' ? false : true; /* 是否有官方抽奖 */
            const item = cardToJson.item || {};
            obj.description = item.content || item.description || ''; /* 转发者的描述 */
            if (obj.type === 1) {
                obj.origin_uid = desc.origin.uid; /* 被转发者的UID */
                obj.origin_rid_str = desc.origin.rid_str /* 被转发者的rid(用于发评论) */
                obj.origin_dynamic_id = desc.orig_dy_id_str; /* 被转发者的动态的ID !!!!此为大数需使用字符串值,不然JSON.parse()会有丢失精度 */
                const { origin_extension } = cardToJson || {};
                obj.origin_hasOfficialLottery = typeof origin_extension === 'undefined' ? false : typeof origin_extension.lott === 'undefined' ? false : true; /* 是否有官方抽奖 */
                const { user, item } = strToJson(cardToJson.origin) || {};
                obj.origin_uname = typeof user === 'undefined' ? '' : user.name || user.uname || ''; /* 被转发者的name */
                obj.origin_description = typeof item === 'undefined' ? '' : item.content || item.description || ''; /* 被转发者的描述 */
            }
            array.push(obj);
        });
    }
    return {
        modifyDynamicResArray: array,
        nextinfo: next
    };
}
function next(tagid) {
    HttpRequest({
        type: 'GET',
        _url: 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_new',
        _query_string: {
            topic_id: tagid 
        },
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
            Accept: 'application/json, text/plain, */*',
            Cookie: "",
        },
        success: chunk => {
            const r = /([\d零一二两三四五六七八九十]+)[.月]([\d零一二两三四五六七八九十]+)[日号]?/;
            modifyDynamicRes(chunk).modifyDynamicResArray.forEach(res=>{
                let des = res.description;
                if (des === '') return;
                const _date = r.exec(des) || [];
                function getTsByMD(month,day) {
                    if (month&&day) {
                        let date = new Date(`${new Date(Date.now()).getFullYear()}-${month}-${day} 23:59:59`).getTime()
                        if (!isNaN(date)) return date / 1000;
                    }
                    return -1
                }
                console.log(getTsByMD(_date[1],_date[2]))
            })
        },
    })
}
next(3230836);
/* 
提取开奖时间
@parm {string} des 描述文字
@return {number} 10位时间戳 | -1
getLotteryNotice = des => {
    const r = /([\d零一二两三四五六七八九十]+)[.月]([\d零一二两三四五六七八九十]+)[日号]?/;
    if (des === '') return -1;
    const _date = r.exec(des) || [];
    return ((month, day) => {
        if (month && day) {
            let date = new Date(`${new Date(Date.now()).getFullYear()}-${month}-${day} 23:59:59`).getTime()
            if (!isNaN(date)) return date / 1000;
        }
        return -1
    })(_date[1], _date[2])
} 
*/
import { buildSimpleCompareBody, readSimple, renderBool } from "/static/modules/cmp_common.js";
export default {
  type: "cmp_contains",
  buildBody(el){ buildSimpleCompareBody(el, "Subcadena (contains)", ""); },
  readConfig: readSimple,
  renderResult: renderBool
};

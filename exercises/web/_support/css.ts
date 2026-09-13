/** Test helper: parse a stylesheet with jsdom's CSSOM and flatten its rules (including @media). */
import { JSDOM } from "jsdom";

export type FlatRule = {
  selector: string;
  media: string | null;
  declarations: Record<string, string>;
  important: string[];
};

export function parseCss(css: string): FlatRule[] {
  const { document } = new JSDOM(`<style>${css}</style>`).window;
  const rules: FlatRule[] = [];
  const visit = (list: CSSRuleList, media: string | null) => {
    for (const rule of Array.from(list)) {
      if ("selectorText" in rule && "style" in rule) {
        const style = (rule as CSSStyleRule).style;
        const declarations: Record<string, string> = {};
        const important: string[] = [];
        for (let i = 0; i < style.length; i++) {
          const name = style[i]!;
          declarations[name] = style.getPropertyValue(name).trim();
          if (style.getPropertyPriority(name)) important.push(name);
        }
        rules.push({ selector: (rule as CSSStyleRule).selectorText, media, declarations, important });
      } else if ("media" in rule && "cssRules" in rule) {
        visit((rule as CSSMediaRule).cssRules, (rule as CSSMediaRule).media.mediaText);
      }
    }
  };
  visit(document.styleSheets[0]!.cssRules, null);
  return rules;
}

/** Rules whose selector list contains `selector` exactly (e.g. ".card" matches ".card, .panel"). */
export function rulesFor(rules: FlatRule[], selector: string, media: string | null = null): FlatRule[] {
  return rules.filter((r) => r.media === media && r.selector.split(",").map((s) => s.trim()).includes(selector));
}

/** Merged declarations for a selector (later rules win), like a tiny cascade for one selector. */
export function declarationsFor(rules: FlatRule[], selector: string, media: string | null = null): Record<string, string> {
  return Object.assign({}, ...rulesFor(rules, selector, media).map((r) => r.declarations));
}

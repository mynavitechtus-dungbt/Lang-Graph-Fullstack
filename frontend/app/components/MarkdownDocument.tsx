import { z } from "zod";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const renderMarkdownSchema = z.object({
  title: z
    .string()
    .optional()
    .describe("Optional short title shown above the document."),
  markdown: z
    .string()
    .describe(
      "Full Markdown body (headings, lists, code fences, tables). Use real newlines between blocks.",
    ),
});

export type RenderMarkdownProps = z.infer<typeof renderMarkdownSchema>;

/**
 * Generative UI: rich MD panel when the agent calls the renderMarkdown tool.
 */
export default function MarkdownDocument({ title, markdown }: RenderMarkdownProps) {
  return (
    <article className="markdown-document rounded-xl border border-zinc-200 bg-zinc-50/80 p-4 shadow-sm">
      {title ? (
        <h2 className="mb-3 border-b border-zinc-200 pb-2 text-lg font-semibold text-zinc-900">
          {title}
        </h2>
      ) : null}
      <div
        className={[
          "prose prose-zinc max-w-none text-[15px] leading-relaxed text-zinc-800",
          "prose-headings:scroll-mt-4 prose-headings:font-semibold prose-headings:text-zinc-900",
          "prose-pre:whitespace-pre-wrap prose-pre:break-words prose-pre:rounded-lg prose-pre:border prose-pre:border-zinc-200 prose-pre:bg-zinc-950 prose-pre:text-zinc-50",
          "prose-code:before:content-none prose-code:after:content-none",
          "prose-a:text-emerald-700",
          "prose-table:block prose-table:overflow-x-auto",
        ].join(" ")}
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </article>
  );
}

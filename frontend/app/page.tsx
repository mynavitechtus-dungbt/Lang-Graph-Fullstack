"use client";

import { CopilotChat, useFrontendTool } from "@copilotkit/react-core/v2";
import MarkdownDocument, { renderMarkdownSchema } from "./components/MarkdownDocument";
import PlanApproval, { showPlanApprovalSchema } from "./components/PlanApproval";
import WeatherCard, { weatherSchema } from "./components/weatherCard";

/** Completes the tool round-trip without re-invoking the agent (avoids stuck loading). */
const noopToolResult = async () => "ok";

export default function Page() {
  useFrontendTool({
    name: "showWeatherCard",
    description: "Display current weather for a city in a card.",
    parameters: weatherSchema,
    handler: noopToolResult,
    followUp: false,
    render: (p) => (
      <WeatherCard
        city={p.args.city ?? ""}
        temperature={p.args.temperature ?? 0}
        condition={p.args.condition ?? ""}
      />
    ),
  });

  useFrontendTool({
    name: "renderMarkdown",
    description:
      "Render a structured Markdown document in the chat (steps, guides, tutorials, long formatted answers). Use when the user wants MD-style content, numbered steps, or a document—not for one-line replies.",
    parameters: renderMarkdownSchema,
    handler: noopToolResult,
    followUp: false,
    render: (p) => (
      <MarkdownDocument title={p.args.title} markdown={p.args.markdown ?? ""} />
    ),
  });

  useFrontendTool({
    name: "showPlanApproval",
    description:
      "After a plan is shown as Markdown, display Yes/No so the user can approve or request changes.",
    parameters: showPlanApprovalSchema,
    handler: noopToolResult,
    followUp: false,
    render: (p) => <PlanApproval question={p.args.question} />,
  });

  return (
    <main className="flex min-h-0 flex-1 flex-col">
      <CopilotChat
        className="min-h-0 flex-1"
        labels={{
          welcomeMessageText: "Agent Get Started",
          chatInputPlaceholder: "What do you want to know?",
          chatDisclaimerText: "AI is always ready to help you. AI never lies.",
        }}
      />
    </main>
  );
}

"use client";

import { z } from "zod";
import { useCopilotChat } from "@copilotkit/react-core";
import { MessageRole, TextMessage } from "@copilotkit/runtime-client-gql";

export const showPlanApprovalSchema = z.object({
  question: z
    .string()
    .optional()
    .describe("Optional short line above the buttons."),
});

export type PlanApprovalProps = z.infer<typeof showPlanApprovalSchema>;

/**
 * Generative UI: Yes / No sends a user message so the LangGraph plan_feedback node can run.
 */
export default function PlanApproval({ question }: PlanApprovalProps) {
  const { appendMessage } = useCopilotChat();

  const send = async (value: "yes" | "no") => {
    await appendMessage(
      new TextMessage({
        role: MessageRole.User,
        content: value,
      }),
    );
  };

  return (
    <div className="mt-3 flex flex-col gap-2 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
      {question ? (
        <p className="text-sm font-medium text-zinc-800">{question}</p>
      ) : (
        <p className="text-sm text-zinc-700">Approve this plan?</p>
      )}
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
          onClick={() => void send("yes")}
        >
          Yes
        </button>
        <button
          type="button"
          className="rounded-lg border border-zinc-300 bg-zinc-50 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-100"
          onClick={() => void send("no")}
        >
          No
        </button>
      </div>
    </div>
  );
}

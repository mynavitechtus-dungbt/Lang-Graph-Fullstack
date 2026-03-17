import {
    CopilotRuntime,
    ExperimentalEmptyAdapter,
    copilotRuntimeNextJSAppRouterEndpoint,
  } from "@copilotkit/runtime";
  import { LangGraphAgent } from "@copilotkit/runtime/langgraph";
  import { NextRequest } from "next/server";
  
  const serviceAdapter = new ExperimentalEmptyAdapter();
  
  const runtime = new CopilotRuntime({
    agents: {
      basic_agent: new LangGraphAgent({
        deploymentUrl:  process.env.LANGGRAPH_DEPLOYMENT_URL || "",
        graphId: "basic_agent",
        langsmithApiKey: process.env.LANGSMITH_API_KEY || "",
      }),
      human_in_the_loop: new LangGraphAgent({
        deploymentUrl:  process.env.LANGGRAPH_DEPLOYMENT_URL || "",
        graphId: "human_in_the_loop",
        langsmithApiKey: process.env.LANGSMITH_API_KEY || "",
      }),
    }
  });
  
  export const POST = async (req: NextRequest) => {
    const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
      runtime,
      serviceAdapter,
      endpoint: "/api/copilotkit",
    });
  
    return handleRequest(req);
  };
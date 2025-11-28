import { streamText, CoreMessage , smoothStream} from 'ai';
import { getSystemPrompt } from '@/app/chat/lib/ai/prompts/system-prompt';
import { querySupabaseTool } from '@/app/chat/lib/ai/tools/query-supabase';
import { generateChart } from '@/app/chat/lib/ai/tools/generate-chart';
import { tavilySearchTool } from '@/app/chat/lib/ai/tools/tavily-search';
import { generateImage } from '@/app/chat/lib/ai/tools/generate-image';
import { makeApiRequestTool } from '@/app/chat/lib/ai/tools/make-api-request';
import { myProvider } from '@/app/chat/lib/ai/providers/providers';
import { getUser } from '@/app/chat/hooks/get-user';
import { getAllMCPTools } from '@/app/chat/lib/simple-mcp-manager';
import { experimental_createMCPClient } from 'ai';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';



export const maxDuration = 30;

export async function POST(req: Request) {
  try {
    const user = await getUser();

    if (!user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { messages, data, selectedModel }: { messages: CoreMessage[], data: any, selectedModel: string } = await req.json();
    const systemPrompt = await getSystemPrompt(user);
    console.log(selectedModel);

    // Get MCP tools
    const mcpTools = await getAllMCPTools();

    const result = streamText({
      model: myProvider.languageModel(selectedModel as any),
      system: systemPrompt,
      messages,
      tools: {
        querySupabase: querySupabaseTool,
        generateChart: generateChart,
        tavilySearch: tavilySearchTool,
        generateImage: generateImage,
        makeApiRequest: makeApiRequestTool,
        ...mcpTools, 
      },
      maxSteps: 10, 
      onError: (error) => {
        console.error('Error:', error);
      },
      experimental_transform: smoothStream({
        chunking: 'word',
      }),
      toolCallStreaming: true,
    });

    // Stream the response back to the client so `useChat` can consume it
    return result.toDataStreamResponse();
  } catch (error: any) {
    console.error('[API] Error:', error);
    return new Response(JSON.stringify({ error: error.message || 'An unexpected error occurred.' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

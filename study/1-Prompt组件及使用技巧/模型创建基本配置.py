# 在internal/handler/app_handler.py
llm = ChatOpenAI(
    model="google/gemini-2.5-pro-exp-03-25:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)

# OpenAIEmbeddings配置为使用硅基流动的API
embedding = OpenAIEmbeddings(
    model="BAAI/bge-large-zh-v1.5",  # 使用硅基流动支持的模型
    openai_api_key=os.getenv("SILICONE_FLOW_API_KEY"),
    openai_api_base=os.getenv("SILICONE_FLOW_BASE_URL"),
)

client = weaviate.connect_to_wcs(
    cluster_url="https://stqzdpo0sykh8wtvamr5g.c0.asia-southeast1.gcp.weaviate.cloud",
    auth_credentials=AuthApiKey("kNhnmiYNikkgyrVVIbTWudrdIioU0tobSGTM"),
)
# **在vector_database_service.py中**
self.client = weaviate.connect_to_wcs(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
)

self.vector_store = WeaviateVectorStore(
    client=self.client,
    index_name="Dataset",
    text_key="text",
    embedding=OpenAIEmbeddings(
        model="BAAI/bge-large-zh-v1.5",  # 使用硅基流动支持的模型
        openai_api_key=os.getenv("SILICONE_FLOW_API_KEY"),
        openai_api_base=os.getenv("SILICONE_FLOW_BASE_URL"),
    )
)

# dalle3需改为，记得引入basemodel和Type
class Dalle3ArgsSchema(BaseModel):
    query: str = Field(description="输入应该是生成图像的文本提示(prompt)")


class SiliconFlowKuaishouTool(BaseTool):
    name: str = "dalle3"
    description: str = "用于生成图像的硅基流动平台上的快手模型"
    args_schema: Type[BaseModel] = Dalle3ArgsSchema

    def _run(self, query: str) -> str:
        # 调用硅基流动API的逻辑
        api_url = "https://api.siliconflow.cn/v1/images/generations"

        try:
            response = requests.post(
                api_url,
                json={"prompt": query},
                headers={"Authorization": "Bearer sk-phhrxiymzriebrcmsrlnlyacgesmqcklretubdbuobwkbejs"}  # 需要替换为实际的API密钥
            )
            response.raise_for_status()
            result = response.json()
            return result.get("image_url", "图像生成失败")
        except Exception as e:
            return f"调用硅基流动API失败: {str(e)}"

    def _arun(self, query: str) -> str:
        return self._run(query)


@add_attribute("args_schema", Dalle3ArgsSchema)
def dalle3(**kwargs) -> BaseTool:
    """返回dalle3绘图的LangChain工具"""
    return SiliconFlowKuaishouTool()

# 另外为了保证最后能关闭weaviate连接，需要更改以下内容
# 1.在vector_database_service.py中，新增以下方法
    def close(self):
        """关闭向量数据库连接"""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
                self.client = None
                # 可选 - 输出日志确认关闭
                print("Weaviate连接已关闭")
        except Exception as e:
            print(f"关闭Weaviate连接时出错: {e}")
# 2.在app.http.app.py中，新增以下代码（在if __name__ == "__main__":之前,app=Http()之后），记得引入对应库
def shutdown_vector_db():
    """应用终止时关闭向量数据库连接"""
    vector_db_service = injector.get(VectorDatabaseService)
    if vector_db_service:
        vector_db_service.close()
        print("应用终止 - Weaviate连接已关闭")

atexit.register(shutdown_vector_db)
# 3.在app.http.module.py中，新增以下代码,同时引入有关库
from injector import Module, Binder, singleton

from internal.service.vector_database_service import VectorDatabaseService
binder.bind(VectorDatabaseService, to=VectorDatabaseService(), scope=singleton)
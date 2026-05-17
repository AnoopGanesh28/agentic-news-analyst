import httpx
import asyncio
import json
import time
import sys

async def main():
    print("[+] Testing Agentic News Analyst API")
    
    # 1. Start Analysis
    print("\n1. Starting analysis...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/analyze",
                json={"topic": "AI in European Regulation"}
            )
            response.raise_for_status()
            data = response.json()
            run_id = data.get("run_id")
            print(f"  -> Run started successfully. Run ID: {run_id}")
        except Exception as e:
            print(f"Failed to start analysis: {e}")
            return

    # 2. Stream Results
    print("\n2. Connecting to SSE Stream...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            async with client.stream("GET", f"http://localhost:8000/api/analyze/{run_id}/stream") as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        print(f"  [Stream] {chunk.strip()}")
                        if "event\": \"done\"" in chunk:
                            print("  -> Stream completed.")
                            break
        except Exception as e:
            print(f"Stream error: {e}")
            return

    # 3. Fetch Report
    print("\n3. Fetching final report...")
    # Wait a tiny bit to ensure state is committed
    time.sleep(1)
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"http://localhost:8000/api/analyze/{run_id}/report")
            response.raise_for_status()
            report_data = response.json()
            print(f"  -> Report length: {len(report_data.get('report', ''))} characters")
        except Exception as e:
            print(f"Failed to fetch report: {e}")

    # 4. List Runs
    print("\n4. Listing past runs...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/runs")
            response.raise_for_status()
            runs = response.json().get("runs", [])
            print(f"  -> Total runs tracked: {len(runs)}")
        except Exception as e:
            print(f"Failed to list runs: {e}")

if __name__ == "__main__":
    asyncio.run(main())

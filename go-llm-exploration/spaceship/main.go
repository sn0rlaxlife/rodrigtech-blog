package main

import (
  "bufio"
  "bytes"
  "encoding/json"
  "fmt"
  "io"
  "net/http"
  "os"

  "github.com/joho/godotenv"
)

// Add costs for model (likely to change)
const costPerMillionToken = 0.15
const costPerMillionOutputToken = 0.6

// Message represents the single turn to the LLM
type Message struct {
  Role  string `json: "role"`
  Content string `json:"content"`
}

// Responses
type LLMRequest struct {
  Messages            []Message `json:"messages"`
  MaxCompletionsToken int        `json:"max_completion_tokens"`
  Temperature         float64    `json:"temperature"`
  TopP                float64    `json:"top_p"`
  FrequencyPenalty    float64    `json:"frequency_penalty"`
  PresencePenalty     float64    `json:"presence_penalty"`
  Model               string     `json:"model"`
}


type LLMResponse struct {
  Choices []struct{
    Messages struct {
        Content string `json:"content"`
      } `json:"message"`
  } `json:"choices"`
  Usage struct {
    TotalTokens       int `json:"total_tokens"`
    CompletionTokens  int `json:"completion_tokens"`
    PromptTokens      int `json:"prompt_tokens"`
  } `json:"usage"`
}

// main function use
func main() {
  // call our env
  err := godotenv.Load()
  if err != nil {
    fmt.Println("Error loading .env file")
    return
  }

  llmKey := os.Getenv("API_KEY")
  endpoint := os.Getenv("AZURE_ENDPOINT") // can be llm endpoint as well will have to update structs

  // Get the user input leverage the bufio
  reader := bufio.NewReader(stdin)
  fmt.Print("Enter your prompt: ")
  userPrompt, _ := reader.ReadString('\n')

  // Prepare the payload using the struct
  payload := LLMRequest {
     Messages: []Message{
       {
            Role:    "user",
            Content:  userPrompt,
        },
      },
      MaxCompletionTokens: 2048,
      Temperature:         1,
      TopP:                1,
      FrequencyPenalty:    0,
      PresencePenalty:     0,
      Model:               "gpt-oss-120b", // could be changed to your model
    }

    // Wrap the payload
    body, err := json.Marshal(payload)
    if err != nil {
       fmt.Prinln("Error marshaling payload:", err)
       return
    }

    // Request paired
    req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(body))
    if err != nil {
       fmt.Println("Error creating request:", err)
       return
    }
    // Set params
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+llmKey)

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        fmt.Println("Error sending request:", err)
        return
    }
    defer resp.Body.Close()

    respBody, err := io.ReadAll(resp.body)
    if err != nil {
         fmt.Println("Error reading response:", err)
         return
    }

    // unmarshall and print the only response
    var llmResp LLMResponse
    if err := json.Unmarshal(respBody, &llmResp); err != nil {
      fmt.Println("Error unmarshaling response:", err)
      fmt.Println(string(respBody)) // fall back if needed
      return
    }

    if len(llmResp.Choices) > 0 {
      fmt.Println("LLM Response:")
      fmt.Println(llmResp.Choices[0].Messages.Content)
      fmt.Printf("Total Tokens: %d\n", llmResp.Usage.TotalTokens)
      costPerToken := costPerMillionToken / 1_000_000
      costPerOutputToken := costPerMillionOutputToken / 1_000_000
      outputCost := float64(llmResp.Usage.CompletionTokens) * costPerOutputToken
      estimatedCost := float64(llmResp.Usage.TotalTokens) * costPerToken
      fmt.Printf("Estimated costs: $%.6f\n", estimatedCost)
      fmt.Printf("Output Cost: $%.6f\n", outputCost)
    } else {
      fmt.Println("No choices found in response")
    }
}


  

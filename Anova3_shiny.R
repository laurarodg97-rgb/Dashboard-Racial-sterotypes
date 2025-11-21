library(shiny)
library(shinydashboard)

ui <- dashboardPage(title= "Sesgos Raciales", skin = "blue", 
  dashboardHeader(
    title = "Sesgos Raciales"
  ), 
  dashboardSidebar(
    sidebarMenu(id = "sidebarID",
                menuItem("Primera Ventana"))
  ), 
  dashboardBody()
)

server <- function(input, output){
  
}

shinyApp(ui, server)
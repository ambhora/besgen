#include <__MODULE__/__MODULE__.hpp>

#include <string>

int main()
{
  return __MODULE__::greet("world") == "hello world" ? 0 : 1;
}

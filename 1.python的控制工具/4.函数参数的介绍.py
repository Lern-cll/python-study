def cheeseshop(kind, *arguments, **keywords):
    print("-- Do you have any", kind, "?")
    print("-- I'm sorry, we're all out of", kind)
    for arg in arguments:
        print(arg)
    print("-" * 40)
    for kw in keywords:
        print(kw, ":", keywords[kw])



cheeseshop("Limburger", "It's very runny, sir.",
           "It's really very, VERY runny, sir.",
           shopkeeper="Michael Palin",
           client="John Cleese",
           sketch="Cheese Shop Sketch")


# lambda的函数使用
def fn(x):
    return lambda n: x * n
fn1 = fn(10)
print(fn1(2))


def my_fn():
    """Do nothing, but document it.

        No, really, it doesn't do anything:

        >>> my_fn()
        >>>
    """
    pass
print(my_fn.__doc__)

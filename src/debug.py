import inspect
from threading import Lock, current_thread

_Ld = Lock()


def printr(obj, *args, **kwargs):
    print(obj, *args, **kwargs)
    return obj


def println():
    frame = inspect.stack()[1]
    thread = current_thread()
    print(f"<#{thread.name} @{frame.function} {frame.filename}:{frame.lineno}>")


def interactive(global_vars, local_vars):
    with _Ld:
        g, l = global_vars, local_vars
        x = ""
        frame = inspect.stack()[1]
        thread = current_thread()
        print(f"[Debug: #{thread.name} @{frame.function} {frame.filename}:{frame.lineno}]")
        while True:
            try:
                s = input()
                if s.endswith(" \\"):
                    s = s[:-2]
                    x += s + "\n"
                    continue
                elif s.strip() == "#cancel":
                    x = ""
                    continue
                else:
                    x += s
            except KeyboardInterrupt:
                return
            except Exception as ex:
                print(ex)
                return
            try:
                if x.startswith("="):
                    x = x[1:]
                    print(eval(x, g, l))
                elif x.strip() == "#return":
                    return g, l
                else:
                    exec(x, g, l)
            except Exception as ex:
                print(ex)
            finally:
                x = ""


if __name__ == "__main__":
    a = 1
    interactive(globals(), locals())

---
title: "Kubernetes Locally with kind"
summary: kind runs a whole Kubernetes cluster inside Docker on your laptop — a free, throwaway practice cluster. Create one, deploy an app, watch it self-heal and scale, then delete it, all without a cloud account or a bill.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 100
tags: [kubernetes, kind, local, hands-on, devops]
lastReviewed: 2026-09
awsCost: free
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **kind** is and why it's the safe way to learn Kubernetes
- The everyday **kubectl** commands: apply, get, scale, delete
- How to write a tiny **Deployment** and **Service** in YAML
- How to *watch* self-healing and scaling happen with your own eyes
- Why you always **delete the cluster** when you're done

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **kind** | Kubernetes running inside Docker on your laptop | Kubernetes lokal di Docker |
| **Cluster** | The whole set of machines Kubernetes manages (here, fake ones) | Sekumpulan mesin |
| **kubectl** | The command-line tool you use to talk to Kubernetes | Alat perintah Kubernetes |
| **Manifest** | A YAML file describing what you want (a Deployment, a Service) | Berkas keinginan (YAML) |
| **apply** | Send a manifest to the cluster: "make this real" | Terapkan keinginan |
| **Replica** | One running copy of a pod | Satu salinan |

## 🧠 The big idea

Learning Kubernetes on real cloud machines is like learning to drive by renting a real car on a real highway — expensive, slow to set up, and a mistake costs money. **kind** (Kubernetes IN Docker) is the **driving simulator**: it runs an entire little Kubernetes cluster *inside Docker containers on your laptop*. Same steering wheel, same pedals, same commands as the real thing — but free, instant to create, and safe to crash. When you're done, you delete the whole cluster and nothing is left behind.

This is exactly the "run it locally first" idea you've used all through Module 5: practise where mistakes are free, before touching anything that bills.

## ❓ Why it matters

Kubernetes has a reputation for being hard, and a lot of that fear comes from learning it in the wrong place — on a real cloud cluster where every experiment is slow, costs money, and feels risky. So people never *play*, and they never build the muscle memory.

kind removes all of that. A cluster appears in about a minute, costs nothing, and can be thrown away and remade instantly. That means you can do the one thing that actually teaches Kubernetes: **break it on purpose and watch it heal.** Delete a pod and see a new one appear. Change "3 replicas" to "6" and watch three more start. Once you've *seen* the control loop from the last lesson do its job in front of you, the concepts stop being abstract. And because it's the real `kubectl` with real manifests, everything you learn here works unchanged on a real cloud cluster later — you just point the same commands at a bigger, paid cluster.

## 📖 Step by step

### 1. What you need

- **Docker** running (you have it from Week 1) — kind builds its fake cluster out of Docker containers.
- **kind** and **kubectl** installed. On macOS with Homebrew: `brew install kind kubectl`. (See the official install pages linked below for other systems.)

### 2. Create a throwaway cluster

```bash
kind create cluster --name practice
```

In about a minute you have a working Kubernetes cluster. Check it's alive:

```bash
kubectl get nodes
# NAME                     STATUS   ROLES           AGE   VERSION
# practice-control-plane   Ready    control-plane   1m    v1.31.x
```

That "node" is a Docker container pretending to be a machine. Good enough to learn everything.

### 3. Describe what you want (a manifest)

Create `app.yaml` — a Deployment asking for **3 copies** of a tiny web server, plus a Service to give them one address:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3                 # I want 3 copies, always
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web                  # send traffic to pods labelled app=web
  ports:
    - port: 80
      targetPort: 80
```

This is the desired state from the last lesson, written down.

### 4. Make it real, and look

```bash
kubectl apply -f app.yaml     # "make this true"
kubectl get pods              # watch 3 pods appear
# web-xxxx   Running
# web-yyyy   Running
# web-zzzz   Running
```

You never told Kubernetes *how* to start three containers — you described the end state and it did the steps.

### 5. Watch self-healing (the fun part)

Delete one pod and immediately look again:

```bash
kubectl delete pod <one-pod-name>
kubectl get pods              # still 3! a new one is already starting
```

You removed a copy; actual dropped to 2; the control loop noticed and started a replacement — no human involved. That's the whole last lesson, happening in front of you.

### 6. Scale by changing the desired number

```bash
kubectl scale deployment web --replicas=6
kubectl get pods              # now 6
```

You changed *what you want* from 3 to 6; the loop started three more. Scaling down works the same way.

### 7. Always clean up

```bash
kind delete cluster --name practice
```

The whole cluster — every pod, node and network — vanishes. Nothing is left running, nothing to forget about. This is the local-first habit: create, experiment, destroy.

### Choosing your setup

- ✅ Learning Kubernetes, testing manifests, running CI checks → kind (free, instant, throwaway).
- ✅ A quick local demo of an app that expects Kubernetes.
- 🚫 Real users / production → a managed cloud cluster (EKS), not kind on your laptop.
- 🚫 Storing data you care about inside a kind cluster — it's disposable by design.

## ⚠️ Common mistakes

- Forgetting to **delete the cluster**, leaving Docker containers eating memory in the background.
- Editing a running pod by hand instead of changing the **manifest** and re-applying — your change vanishes when the loop replaces the pod.
- Expecting data stored in a pod to survive — pods are disposable; a deleted pod's local files are gone.
- Treating kind as production. It's a simulator: perfect for learning, wrong for real traffic.
- Skipping the "delete a pod and watch it heal" step — that's the exercise that makes it click.

## 🏆 Best practices

- [ ] Keep your desired state in **YAML manifests** under version control; change the file, re-apply.
- [ ] Use kind for learning, demos and CI — free and reproducible.
- [ ] **Delete the cluster** when you're done (create → experiment → destroy).
- [ ] Prove the same manifests work on kind before running them on a paid cluster.
- [ ] Never keep data you care about inside a disposable cluster.

:::revoshop
1. **Manifest for RevoShop.** Sketch a Deployment for the RevoShop API: how many replicas, which image, which port. What single line would you change to run 5 copies instead of 3?
2. **Try it (optional, free).** If you have Docker free, spin up a kind cluster and deploy the `nginx` example above. Delete a pod and watch it come back. That five-minute experiment teaches more than an hour of reading.
3. **The stateful problem.** RevoShop needs PostgreSQL and Redis. Why is running *those* inside disposable pods risky, and where does their data really belong (hint: Week 3's RDS, and a managed Redis)?
4. **Local vs real.** Which of your kind commands would work unchanged against a real EKS cluster, and what changes (hint: not the commands — the cost and who can reach it)?
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why you'd learn Kubernetes on kind before touching a real cloud cluster — using the driving-simulator analogy — and what "delete a pod and watch it come back" demonstrates about the control loop.

## 📐 Design it

Write (on paper or in a real `app.yaml`) the desired state for a small web app: a Deployment with a chosen replica count and image, and a Service in front. Then list the exact `kubectl`/`kind` commands you'd run to create the cluster, apply it, scale it to 6, and tear it all down.

:::quiz
Show a possible answer

Manifest: a Deployment `web` with `replicas: 3`, image `nginx:1.27-alpine`, port 80, plus a Service selecting `app: web` on port 80. Commands: `kind create cluster --name practice` → `kubectl apply -f app.yaml` → `kubectl get pods` (see 3) → `kubectl scale deployment web --replicas=6` (see 6) → `kind delete cluster --name practice` (all gone). To prove self-healing in between: `kubectl delete pod <name>` then `kubectl get pods` — still the target count, because the loop replaced it.
:::

### 📝 Self-review checklist

- [ ] The manifest states a replica count and an image
- [ ] I know the create → apply → scale → delete commands
- [ ] I planned to delete the cluster at the end

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

### 🧪 Hands-on: make Kubernetes heal in front of you

No Python here — the exercise is to *use* it. If you have Docker running (free):

1. `kind create cluster --name practice`
2. Save the `app.yaml` from step 3 above and `kubectl apply -f app.yaml`.
3. `kubectl get pods` — confirm 3 are Running.
4. `kubectl delete pod <one-name>` then immediately `kubectl get pods` again. **Watch a replacement appear.** Write down what you saw.
5. `kubectl scale deployment web --replicas=6`, confirm 6, then back to `--replicas=2`.
6. `kind delete cluster --name practice`. Confirm with `kubectl get nodes` (it will error — the cluster is gone).

No Docker right now? Do it as a paper trace: for each command, write what `kubectl get pods` would show afterwards.

## ✅ Quick check

:::quiz
Why is kind a good place to learn Kubernetes, but a bad place to run real traffic?

kind runs a whole cluster inside Docker on your laptop — free, instant, and throwaway — so you can experiment and break things safely, and the commands are identical to a real cluster. But it's a single laptop pretending to be many machines: no real availability, not reachable by users, and disposable by design. Real traffic needs a managed cloud cluster (EKS).
:::

:::quiz
You edit a running pod by hand to change a setting, and a moment later your change is gone. Why?

Pods are disposable and managed by the control loop. If that pod is replaced (it crashed, or you deleted it, or a rollout happened), the new pod is created from the **manifest**, not from your hand-edit. To make a change stick, edit the YAML and re-apply it — that changes the desired state the loop rebuilds from.
:::

## 📚 Keep learning

- [kind: Quick start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl: Cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

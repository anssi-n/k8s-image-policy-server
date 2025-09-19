from pydantic import BaseModel, model_serializer
'''
{
  "apiVersion": "imagepolicy.k8s.io/v1alpha1",
  "kind": "ImageReview",
  "spec": {
    "containers": [
      {
        "image": "myrepo/myimage:v1"
      },
      {
        "image": "myrepo/myimage@sha256:beb6bd6a68f114c1dc2ea4b28db81bdf91de202a9014972bec5e4d9171d90ed"
      }
    ],
    "annotations": {
      "mycluster.image-policy.k8s.io/ticket-1234": "break-glass"
    },
    "namespace": "mynamespace"
  }
}
'''
class Container(BaseModel):
    image: str

class Spec(BaseModel):
    containers: list[Container]
    annotations: dict[str,str] | None = None
    namespace: str

class ImageReviewRequest(BaseModel):
    apiVersion: str
    kind: str = "ImageReview"
    spec: Spec

class ImageReviewStatus(BaseModel):
    @model_serializer
    def _serialize(self):
        return {k: v for k,v in self if v is not None}
    
    allowed: bool
    reason: str | None = None

class ImageReviewResponse(BaseModel):
    apiVersion: str
    kind: str = "ImageReview"
    status: ImageReviewStatus